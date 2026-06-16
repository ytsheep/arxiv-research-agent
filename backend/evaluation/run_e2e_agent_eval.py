"""Run full-chain Single-Agent and Multi-Agent evaluation from the chat entrypoint."""

from __future__ import annotations

import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agent.orchestrator import AgentOrchestrator
from app.tools.llm_client import llm_client


EVAL_ROOT = Path(__file__).resolve().parent
CASES_PATH = EVAL_ROOT / "cases" / "e2e_agent_cases.jsonl"
OUTPUT_ROOT = EVAL_ROOT / "outputs"

STAGE_TO_SKILL = {
    "supervisor_planning": "Supervisor",
    "react_tool_selection": "ControlledReAct",
    "react_fallback_planning": "ControlledReAct",
    "legacy_react_planning": "ControlledReAct",
    "paper_card_summary": "paper_search_card_skill",
    "paper_comparison": "paper_compare_skill",
    "paper_selection": "paper_select_best_skill",
    "literature_survey": "literature_survey_skill",
    "paper_deep_report": "paper_deep_read_skill",
    "final_composition": "FinalComposer",
    "unclassified": "unclassified",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def merge_usage(
    target: dict[str, dict[str, int]],
    name: str,
    usage: dict[str, int],
) -> None:
    bucket = target.setdefault(
        name,
        {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    )
    for key in bucket:
        bucket[key] += int(usage.get(key, 0))


def skill_usage_from_stages(stages: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    skills: dict[str, dict[str, int]] = {}
    for stage, usage in stages.items():
        merge_usage(skills, STAGE_TO_SKILL.get(stage, stage), usage)
    return skills


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stage_usage: dict[str, dict[str, int]] = {}
    skill_usage: dict[str, dict[str, int]] = {}
    for row in rows:
        for stage, usage in row.get("usage_by_stage", {}).items():
            merge_usage(stage_usage, stage, usage)
        for skill, usage in row.get("usage_by_skill", {}).items():
            merge_usage(skill_usage, skill, usage)

    sorted_stages = dict(
        sorted(stage_usage.items(), key=lambda item: item[1]["total_tokens"], reverse=True)
    )
    sorted_skills = dict(
        sorted(skill_usage.items(), key=lambda item: item[1]["total_tokens"], reverse=True)
    )
    return {
        "cases": len(rows),
        "completed_cases": sum(bool(row.get("completed")) for row in rows),
        "completion_rate": round(
            sum(bool(row.get("completed")) for row in rows) / len(rows), 4
        ) if rows else 0.0,
        "task_count_accuracy": round(
            sum(bool(row.get("task_count_correct")) for row in rows) / len(rows), 4
        ) if rows else 0.0,
        "avg_latency_ms": mean([row.get("latency_ms", 0.0) for row in rows]),
        "avg_input_tokens": mean([row.get("input_tokens", 0) for row in rows]),
        "avg_output_tokens": mean([row.get("output_tokens", 0) for row in rows]),
        "avg_total_tokens": mean([row.get("total_tokens", 0) for row in rows]),
        "total_tokens": sum(row.get("total_tokens", 0) for row in rows),
        "token_usage_by_stage": sorted_stages,
        "token_usage_by_skill": sorted_skills,
    }


async def main() -> None:
    runs: list[dict[str, Any]] = []
    run_id = int(time.time())
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    args = parser.parse_args()
    cases = read_jsonl(CASES_PATH)
    if args.case:
        cases = [case for case in cases if case["case_id"] == args.case]

    def save_current() -> None:
        single = [row for row in runs if row["agent_mode"] == "single_agent"]
        multi = [row for row in runs if row["agent_mode"] == "multi_agent"]
        metrics = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "benchmark_scope": "full_chain_from_chat_entrypoint_to_final_response",
            "per_case_timeout_seconds": args.timeout_seconds,
            "total_cases": len(runs),
            "single_agent": summarize(single),
            "multi_agent": summarize(multi),
            "overall": summarize(runs),
            "embedding_cold_start_comparison": {
                "cold_search_latency_ms": next(
                    (row.get("latency_ms", 0.0) for row in runs if row.get("cold_start_probe")),
                    0.0,
                ),
                "warm_search_latency_ms": next(
                    (
                        row.get("latency_ms", 0.0)
                        for row in runs
                        if row.get("case_id") == "e2e_single_search_warm"
                    ),
                    0.0,
                ),
            },
        }
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        write_jsonl(OUTPUT_ROOT / "e2e_agent_runs.jsonl", runs)
        with (OUTPUT_ROOT / "e2e_agent_metrics.json").open("w", encoding="utf-8") as file:
            json.dump(metrics, file, ensure_ascii=False, indent=2)

    orchestrator = AgentOrchestrator()
    try:
        for case in cases:
            print(f"[E2E] start {case['case_id']}", flush=True)
            llm_client.reset_usage()
            session_id = f"eval_e2e_{run_id}_{case['case_id']}"
            started = time.perf_counter()
            result: dict[str, Any] = {
                "case_id": case["case_id"],
                "agent_mode": case["agent_mode"],
                "user_query": case["user_query"],
                "session_id": session_id,
                "expected_task_count": int(case.get("expected_task_count", 1)),
                "cold_start_probe": bool(case.get("cold_start_probe", False)),
            }
            try:
                response = await asyncio.wait_for(
                    orchestrator.handle_chat(case["user_query"], session_id),
                    timeout=args.timeout_seconds,
                )
                papers = getattr(response, "papers", []) or []
                response_type = getattr(response, "type", "")
                success = bool(getattr(response, "success", False))
                metadata = getattr(response, "metadata", {}) or {}
                task_summary = metadata.get("task_summary", [])
                actual_task_types = [
                    task.get("task_type", "")
                    for task in task_summary
                    if task.get("task_type") != "final_summary"
                ]
                workflow_tasks_complete = all(
                    task.get("status") == "completed"
                    for task in task_summary
                    if task.get("task_type") != "final_summary"
                )
                expected_types = case.get("expected_response_types", [])
                min_papers = int(case.get("min_papers", 0))
                expected_task_count = int(case.get("expected_task_count", 1))
                actual_task_count = len(actual_task_types) if task_summary else 1
                task_count_correct = actual_task_count == expected_task_count
                result.update({
                    "success": success,
                    "trace_id": getattr(response, "trace_id", ""),
                    "response_type": response_type,
                    "paper_count": len(papers),
                    "expected_task_count": expected_task_count,
                    "actual_task_count": actual_task_count,
                    "actual_task_types": actual_task_types,
                    "task_count_correct": task_count_correct,
                    "workflow_tasks_complete": workflow_tasks_complete if task_summary else True,
                    "cold_start_probe": bool(case.get("cold_start_probe", False)),
                    "completed": (
                        success
                        and response_type in expected_types
                        and len(papers) >= min_papers
                        and task_count_correct
                        and (workflow_tasks_complete if task_summary else True)
                    ),
                })
            except asyncio.TimeoutError:
                result.update({
                    "success": False,
                    "completed": False,
                    "status": "timeout",
                    "error": f"Exceeded {args.timeout_seconds}s per-case timeout",
                })
            except Exception as exc:
                result.update({
                    "success": False,
                    "completed": False,
                    "error": str(exc),
                })
            result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            usage = llm_client.get_usage()
            result.update(usage)
            result["usage_by_skill"] = skill_usage_from_stages(
                usage.get("usage_by_stage", {})
            )
            runs.append(result)
            save_current()
            print(
                f"[E2E] done {case['case_id']} completed={result.get('completed')} "
                f"latency_ms={result['latency_ms']} tokens={result.get('total_tokens', 0)}",
                flush=True,
            )

        save_current()
        print((OUTPUT_ROOT / "e2e_agent_metrics.json").read_text(encoding="utf-8"))
    finally:
        await orchestrator.close()
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())

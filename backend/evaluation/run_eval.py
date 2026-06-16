"""Run the lightweight paper Agent evaluation suite."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agent.executor.execution_map import EXECUTION_MAP
from app.agent.orchestrator import AgentOrchestrator
from app.tools.arxiv_tool import ArxivTool
from app.tools.llm_client import llm_client
from app.tools.pdf_tool import PdfTool


EVAL_ROOT = Path(__file__).resolve().parent
CASES_ROOT = EVAL_ROOT / "cases"
DEFAULT_OUTPUT_ROOT = EVAL_ROOT / "outputs"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_arxiv_id(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id.strip().lower())


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\ufffd", "")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    return " ".join(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


class EvaluationRunner:
    def __init__(self, output_root: Path):
        self.output_root = output_root
        self.orchestrator = AgentOrchestrator()
        self.arxiv_tool = ArxivTool()
        self.pdf_tool = PdfTool()
        self.runs: list[dict[str, Any]] = []
        self.pdf_document_runs: list[dict[str, Any]] = []

    async def close(self) -> None:
        await self.arxiv_tool.close()
        await self.pdf_tool.close()
        await self.orchestrator.close()
        await llm_client.close()

    async def run_agent(self) -> None:
        for case in read_jsonl(CASES_ROOT / "agent_cases.jsonl"):
            started = time.perf_counter()
            llm_client.reset_usage()
            result: dict[str, Any] = {
                "eval_type": "agent",
                "case_id": case["case_id"],
                "user_query": case["user_query"],
            }
            try:
                actual_route = self.orchestrator._detect_complexity(case["user_query"])
                actual_intent = ""
                actual_task_types: list[str] = []
                actual_capabilities: list[str] = []

                if actual_route == "simple":
                    state = {
                        "user_message": case["user_query"],
                        "last_papers": case.get("last_papers", []),
                        "interest_query": case.get("interest_query", "machine learning"),
                    }
                    classified = await self.orchestrator.graph_runner._classify_intent_node(state)
                    actual_intent = classified.get("intent", "")
                    selected = classified.get("selected_skill", "")
                    if selected:
                        actual_capabilities.append(selected)
                else:
                    actual_intent = "compound_workflow"
                    planned = await self.orchestrator.multi_agent_runner.planner.plan(
                        case["user_query"], {}, [],
                    )
                    actual_task_types = [
                        item.get("task_type", "")
                        for item in planned.get("task_plan", [])
                        if item.get("task_type")
                    ]
                    for task_type in actual_task_types:
                        if task_type in EXECUTION_MAP:
                            capability = EXECUTION_MAP[task_type][0]
                            if capability != "_final_summary" and capability not in actual_capabilities:
                                actual_capabilities.append(capability)

                required = set(case.get("required_capabilities", []))
                forbidden = set(case.get("forbidden_capabilities", []))
                actual = set(actual_capabilities)
                route_correct = actual_route == case["expected_route"]
                intent_correct = actual_intent == case["expected_intent"]
                dispatch_correct = (
                    route_correct
                    and required.issubset(actual)
                    and forbidden.isdisjoint(actual)
                    and all(name in self.orchestrator.tool_registry for name in actual)
                )

                result.update({
                    "agent_mode": "single_agent" if actual_route == "simple" else "multi_agent",
                    "expected_route": case["expected_route"],
                    "actual_route": actual_route,
                    "route_correct": route_correct,
                    "expected_intent": case["expected_intent"],
                    "actual_intent": actual_intent,
                    "intent_correct": intent_correct,
                    "required_capabilities": sorted(required),
                    "actual_capabilities": actual_capabilities,
                    "actual_task_types": actual_task_types,
                    "dispatch_correct": dispatch_correct,
                    "status": "success",
                })
            except Exception as exc:
                result.update({"status": "error", "error": str(exc)})
            result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            result.update(llm_client.get_usage())
            self.runs.append(result)

    async def run_retrieval(self) -> None:
        for index, case in enumerate(read_jsonl(CASES_ROOT / "retrieval_cases.jsonl")):
            if index > 0:
                await asyncio.sleep(3.1)
            started = time.perf_counter()
            llm_client.reset_usage()
            result: dict[str, Any] = {
                "eval_type": "retrieval",
                "case_id": case["case_id"],
                "query": case["query"],
            }
            try:
                response = {}
                attempts = 0
                for attempt in range(1, 4):
                    attempts = attempt
                    response = await self.arxiv_tool.search(case["query"], max_results=3)
                    if response.get("success") or "429" not in str(response.get("error", "")):
                        break
                    await asyncio.sleep(10 * attempt)
                returned = [
                    normalize_arxiv_id(paper.get("arxiv_id", ""))
                    for paper in response.get("papers", [])[:3]
                ]
                gold = [normalize_arxiv_id(value) for value in case["gold_arxiv_ids"]]
                hits = len(set(gold) & set(returned))
                result.update({
                    "gold_arxiv_ids": gold,
                    "returned_arxiv_ids": returned,
                    "recall_at_3": round(hits / len(gold), 4) if gold else 0.0,
                    "cache_hit": response.get("cache_hit", False),
                    "attempts": attempts,
                    "status": "success" if response.get("success") else "error",
                    "error": response.get("error"),
                })
            except Exception as exc:
                result.update({"status": "error", "error": str(exc), "recall_at_3": 0.0})
            result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            result.update(llm_client.get_usage())
            self.runs.append(result)

    async def run_pdf(self) -> None:
        cases = read_jsonl(CASES_ROOT / "pdf_cases.jsonl")
        parse_results: dict[str, dict[str, Any]] = {}
        for case in cases:
            paper_id = case["paper_id"]
            if paper_id in parse_results:
                continue
            pdf_path = BACKEND_ROOT / case["pdf_path"]
            started = time.perf_counter()
            parsed = await self.pdf_tool.parse_full_text(paper_id, str(pdf_path))
            document_result = {
                "paper_id": paper_id,
                "success": parsed.get("success", False),
                "error": parsed.get("error"),
                "section_count": len(parsed.get("sections", [])),
                "parse_latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
            parse_results[paper_id] = document_result
            self.pdf_document_runs.append(document_result)

        for case in cases:
            started = time.perf_counter()
            llm_client.reset_usage()
            result: dict[str, Any] = {
                "eval_type": "pdf",
                "case_id": case["case_id"],
                "paper_id": case["paper_id"],
            }
            try:
                pdf_path = BACKEND_ROOT / case["pdf_path"]
                parsed_path = BACKEND_ROOT / case["parsed_path"]
                parsed_text = normalize_text(parsed_path.read_text(encoding="utf-8")) if parsed_path.exists() else ""
                matches = [
                    normalize_text(snippet) in parsed_text
                    for snippet in case.get("gold_snippets", [])
                ]
                document_result = parse_results.get(case["paper_id"], {})
                parse_correct = (
                    document_result.get("success", False)
                    and pdf_path.exists()
                    and parsed_path.exists()
                    and len(parsed_text) >= case.get("min_parsed_chars", 1000)
                    and sum(matches) >= case.get("min_snippet_matches", 1)
                )
                result.update({
                    "pdf_exists": pdf_path.exists(),
                    "parsed_exists": parsed_path.exists(),
                    "parsed_chars": len(parsed_text),
                    "document_parse_success": document_result.get("success", False),
                    "document_parse_latency_ms": document_result.get("parse_latency_ms", 0.0),
                    "snippet_matches": sum(matches),
                    "snippet_total": len(matches),
                    "parse_correct": parse_correct,
                    "status": "success",
                })
            except Exception as exc:
                result.update({"status": "error", "error": str(exc), "parse_correct": False})
            result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
            result.update(llm_client.get_usage())
            self.runs.append(result)

    def build_metrics(self) -> dict[str, Any]:
        agent = [row for row in self.runs if row["eval_type"] == "agent"]
        single_agent = [row for row in agent if row.get("agent_mode") == "single_agent"]
        multi_agent = [row for row in agent if row.get("agent_mode") == "multi_agent"]
        retrieval = [row for row in self.runs if row["eval_type"] == "retrieval"]
        successful_retrieval = [row for row in retrieval if row.get("status") == "success"]
        pdf = [row for row in self.runs if row["eval_type"] == "pdf"]
        by_type = {}
        for eval_type, rows in (("agent", agent), ("retrieval", retrieval), ("pdf", pdf)):
            by_type[eval_type] = {
                "cases": len(rows),
                "avg_latency_ms": mean([row.get("latency_ms", 0.0) for row in rows]),
                "avg_total_tokens": mean([row.get("total_tokens", 0) for row in rows]),
            }

        def summarize_agent_mode(rows: list[dict[str, Any]]) -> dict[str, Any]:
            stages: dict[str, dict[str, int]] = {}
            for row in rows:
                for stage, usage in row.get("usage_by_stage", {}).items():
                    target = stages.setdefault(
                        stage,
                        {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                    )
                    for key in target:
                        target[key] += int(usage.get(key, 0))
            return {
                "cases": len(rows),
                "avg_latency_ms": mean([row.get("latency_ms", 0.0) for row in rows]),
                "avg_input_tokens": mean([row.get("input_tokens", 0) for row in rows]),
                "avg_output_tokens": mean([row.get("output_tokens", 0) for row in rows]),
                "avg_total_tokens": mean([row.get("total_tokens", 0) for row in rows]),
                "total_tokens": sum(row.get("total_tokens", 0) for row in rows),
                "token_usage_by_stage": stages,
            }

        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent_benchmark_scope": "routing_and_planning_only",
            "total_runs": len(self.runs),
            "agent_cases": len(agent),
            "intent_accuracy": mean([float(row.get("intent_correct", False)) for row in agent]),
            "dispatch_accuracy": mean([float(row.get("dispatch_correct", False)) for row in agent]),
            "agent_by_mode": {
                "single_agent": summarize_agent_mode(single_agent),
                "multi_agent": summarize_agent_mode(multi_agent),
            },
            "retrieval_cases": len(retrieval),
            "retrieval_api_success_rate": round(len(successful_retrieval) / len(retrieval), 4) if retrieval else 0.0,
            "retrieval_recall_at_3": mean([row.get("recall_at_3", 0.0) for row in successful_retrieval]),
            "pdf_cases": len(pdf),
            "pdf_parse_accuracy": mean([float(row.get("parse_correct", False)) for row in pdf]),
            "pdf_documents": len(self.pdf_document_runs),
            "pdf_avg_document_parse_latency_ms": mean([
                row.get("parse_latency_ms", 0.0) for row in self.pdf_document_runs
            ]),
            "avg_latency_ms": mean([row.get("latency_ms", 0.0) for row in self.runs]),
            "avg_input_tokens": mean([row.get("input_tokens", 0) for row in self.runs]),
            "avg_output_tokens": mean([row.get("output_tokens", 0) for row in self.runs]),
            "avg_total_tokens": mean([row.get("total_tokens", 0) for row in self.runs]),
            "total_tokens": sum(row.get("total_tokens", 0) for row in self.runs),
            "by_type": by_type,
        }

    def save(self) -> dict[str, Any]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        metrics = self.build_metrics()
        failures = [
            row for row in self.runs
            if row.get("status") == "error"
            or row.get("intent_correct") is False
            or row.get("dispatch_correct") is False
            or row.get("recall_at_3") == 0
            or row.get("parse_correct") is False
        ]
        write_jsonl(self.output_root / "eval_runs.jsonl", self.runs)
        write_jsonl(self.output_root / "pdf_document_runs.jsonl", self.pdf_document_runs)
        write_jsonl(self.output_root / "eval_failures.jsonl", failures)
        with (self.output_root / "eval_metrics.json").open("w", encoding="utf-8") as file:
            json.dump(metrics, file, ensure_ascii=False, indent=2)
        return metrics


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["agent", "retrieval", "pdf", "all"], default="all")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    runner = EvaluationRunner(args.output_dir)
    try:
        if args.type in ("agent", "all"):
            await runner.run_agent()
        if args.type in ("retrieval", "all"):
            await runner.run_retrieval()
        if args.type in ("pdf", "all"):
            await runner.run_pdf()
        metrics = runner.save()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())

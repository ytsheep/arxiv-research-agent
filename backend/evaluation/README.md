# Lightweight Evaluation

This directory contains a small, interview-oriented evaluation suite for the
paper Agent. It measures only the core capabilities:

1. Intent recognition and task dispatch accuracy.
2. arXiv retrieval Recall@3.
3. PDF parse accuracy.
4. Single-Agent and Multi-Agent routing/planning latency.
5. Per-run and per-LLM-stage provider-reported token usage.

The current fixed test set contains 60 Agent routing/dispatch cases, 40 arXiv
Recall@3 cases, and 30 PDF parsing cases.

The Agent evaluation is side-effect free. It executes the real simple-task
intent node and the real multi-agent Supervisor planner, then validates the
planned Skill/Tool dispatch through `EXECUTION_MAP`. It does not collect or
parse papers. The set includes ambiguous, incomplete, conversational, and
compound requests so that routing accuracy is not inflated by template-like
queries.

The Agent timing benchmark covers routing and planning only. Single-Agent
cases execute the deterministic intent node. Multi-Agent cases execute the
Supervisor planner. It does not execute complete search, comparison, collect,
or deep-read workflows. Token usage is grouped by labeled LLM stage, such as
`supervisor_planning`, `react_tool_selection`, and `paper_deep_report`.

The retrieval evaluation requests three results per query and paces arXiv API
calls to reduce rate limiting. Recall@3 is calculated over successful API
responses only; `retrieval_api_success_rate` separately reports external API
availability.

The PDF evaluation reparses each source PDF with the current `PdfTool`, then
checks 30 deterministic normalized token windows extracted from three local
PDF files against the generated `parsed.md` files. Document parse latency is
recorded once per PDF.

## Full-Chain Agent Evaluation

The end-to-end Agent benchmark starts at `AgentOrchestrator.handle_chat()` and
runs through the real LangGraph, ReAct or Supervisor, Skills, Tools, memory,
checkpointing, and final response. It contains ten representative cases:

1. Four Single-Agent cases covering cold/warm search, deep read, and comparison.
2. Six Multi-Agent cases covering workflows with two, three, or four tasks.

Each case has a 90-second timeout. One Orchestrator is reused across the run so
the first case records BGE-M3 cold-start cost while later cases use the loaded
model. Token usage is reported by LLM stage and mapped Skill. The latest run
completed all four Single-Agent cases and three of six Multi-Agent cases. All
ten cases produced the expected task count. The three incomplete workflows
used Chinese-only arXiv search topics, returned zero candidates, retried once,
and then returned a controlled partial result.

```powershell
cd backend
python evaluation/run_e2e_agent_eval.py
```

Results:

```text
evaluation/outputs/e2e_agent_runs.jsonl
evaluation/outputs/e2e_agent_metrics.json
```

## Generate PDF Cases

```powershell
cd backend
python evaluation/generate_pdf_cases.py
```

## Run

```powershell
cd backend
python evaluation/run_eval.py --type all
```

Supported types are `agent`, `retrieval`, `pdf`, and `all`.

Results are written to:

```text
evaluation/outputs/
  eval_runs.jsonl
  eval_metrics.json
  eval_failures.jsonl
  pdf_document_runs.jsonl
```

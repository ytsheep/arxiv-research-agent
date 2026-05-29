# Claude Code Agent Expansion Implementation Guide

This file is the implementation brief for expanding the current arXiv Research-Agent.
It is intended for Claude Code or any coding agent working in this repository.

## 1. Objective

Upgrade the current paper-search assistant into a research-workflow Agent.

The Agent should support:

```text
1. Paper search.
2. Interest-based paper recommendation.
3. Follow-up references such as "the second paper" or "that previous paper".
4. Deep reading of a selected paper.
5. Multi-paper comparison.
6. Small literature survey generation.
7. User memory/preference management.
8. Trace failure diagnosis.
```

Do not add subscription or notification automation to the Agent. Subscription and
notification must remain manual UI features.

## 2. Current Baseline

Current Tool Registry capabilities:

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
trace_query
paper_search_card_skill
```

Current implemented Skill files:

```text
paper_search_card_skill
trace_diagnosis_skill
```

`trace_diagnosis_skill` exists but should be registered and validated as part of
this expansion.

Current four-layer Memory:

```text
Working Memory:
  PaperAgentState

Short-term Memory:
  chat_messages Messages List by session_id

Long-term Structured Memory:
  SQL tables such as user_preferences, papers, paper_files, subscriptions, tasks, task_steps

Long-term Semantic Memory:
  semantic_memories with embedding_json and TF-IDF fallback
```

## 3. Target Skills

Implement or register these Skills:

```text
paper_search_card_skill
paper_deep_read_skill
paper_compare_skill
literature_survey_skill
interest_recommendation_skill
memory_profile_skill
trace_diagnosis_skill
```

Skill responsibilities:

```text
paper_search_card_skill:
  Search arXiv, rerank candidates, generate paper cards.

paper_deep_read_skill:
  Resolve a paper reference, collect if needed, parse full text, generate report, return report summary.

paper_compare_skill:
  Load selected papers/reports and compare problem, method, experiment, result, limitation, and value.

literature_survey_skill:
  Rewrite/expand a topic, search papers, rerank, summarize, compare, and produce a small survey.

interest_recommendation_skill:
  Use user preferences and semantic memory to recommend papers.

memory_profile_skill:
  Read and update user preferences, including positive and negative interests.

trace_diagnosis_skill:
  Query trace records, fetch trace detail, diagnose failed node/tool/error, and suggest fixes.
```

The ReAct subgraph should prefer Skills over atomic Tools.

## 4. Target Tools

Register these Agent-callable Tools:

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
library_get_paper
library_get_report
paper_collect
paper_parse_full_text
paper_generate_deep_report
semantic_memory_search
user_preference_get
user_preference_update
trace_query
trace_get
```

Do not register these as Agent-callable Tools:

```text
subscription_create
subscription_update
subscription_run_now
notify_send_email
notify_send_feishu
```

They may remain available to manual API/UI flows only.

## 5. Permissions

Use Tool Registry permissions:

```text
read_only:
  arxiv_search
  paper_rerank
  paper_generate_card_summary
  library_search_papers
  library_get_paper
  library_get_report
  semantic_memory_search
  user_preference_get
  trace_query
  trace_get

write_safe:
  paper_collect
  user_preference_update

expensive:
  paper_parse_full_text
  paper_generate_deep_report

external_send:
  none in this phase

write_dangerous:
  none in this phase
```

Business guards:

```text
1. Search must not trigger full-text parsing unless the user explicitly asks for deep reading.
2. Deep reading must resolve a concrete arxiv_id before collecting/parsing.
3. Preference update must summarize what changed.
4. ReAct must not call subscription or notification Tools.
5. Expensive Tools must be max-step-limited and traceable.
```

## 6. Intent Router

Add a structured Intent Router before ReAct planning.

The router must combine:

```text
1. Rule-based high-confidence routing.
2. LLM structured classification with fixed JSON output.
3. Backend validation and clarification when confidence or slots are insufficient.
```

Required output shape:

```json
{
  "intent": "paper_deep_read",
  "selected_skill": "paper_deep_read_skill",
  "confidence": 0.91,
  "slots": {
    "topic": "",
    "paper_ref": "second_last_result",
    "arxiv_id": "",
    "paper_ids": [],
    "top_n": 2
  },
  "needs_clarification": false,
  "rewritten_query": "",
  "query_rewrite_source": "",
  "reason": "User asked to deep-read the second paper from previous results."
}
```

Rules:

```text
confidence >= 0.85:
  execute selected_skill if required slots are valid.

0.7 <= confidence < 0.85:
  allow execution only for read_only tasks with complete slots.

confidence < 0.7:
  ask a clarification question.

missing required slots:
  ask a clarification question.
```

## 7. Query Rewrite

Implement query rewrite as a controlled backend step.

Store in State and Trace:

```text
original_query
rewritten_query
query_rewrite_source
query_filters
```

Rewrite scenarios:

```text
paper search:
  Convert natural request into academic keywords.

interest recommendation:
  Generate query from user_preferences and semantic_memories.

follow-up reference:
  Generate query from the referenced previous paper title, categories, and summary.

literature survey:
  Expand topic into related academic terms.
```

Do not lose the original user message.

## 8. Memory Integration

Use the existing four-layer Memory:

```text
Working Memory:
  PaperAgentState stores intent, slots, rewritten query, selected papers, referenced paper, and observations.

Short-term Memory:
  chat_messages stores current session messages, previous paper cards, and paired tool_call/tool_response groups.

Long-term Structured Memory:
  user_preferences stores preferred_topics, negative preferences, category preferences, and defaults.
  papers and paper_files store paper facts and file state.
  tasks and task_steps store trace facts.

Long-term Semantic Memory:
  semantic_memories stores search_history, paper, report, and preference_summary chunks.
```

New memory Tools should be wrappers around existing memory services:

```text
semantic_memory_search
user_preference_get
user_preference_update
```

## 9. Required User Scenarios

After implementation, these user prompts must work:

```text
1. Find 2 papers about agent memory.
2. Find papers similar to the second one.
3. Deep-read the second paper and generate a report.
4. Compare these two papers.
5. Make a small literature survey about RAG agents.
6. Find two papers I am interested in.
7. In the future, recommend more RAG Agent papers and fewer CV papers.
8. Why did the last task fail?
```

Expected routing:

```text
Find 2 papers about agent memory:
  paper_search_card_skill

Find papers similar to the second one:
  resolve previous paper -> query rewrite -> paper_search_card_skill

Deep-read the second paper:
  paper_deep_read_skill

Compare these two papers:
  paper_compare_skill

Make a small literature survey:
  literature_survey_skill

Find papers I am interested in:
  interest_recommendation_skill

Recommend more RAG Agent and fewer CV:
  memory_profile_skill

Why did the last task fail:
  trace_diagnosis_skill
```

## 10. Verification Requirements

Claude Code must verify existing functionality and new functionality.

Backend:

```bash
cd backend
python -m compileall app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
curl http://localhost:8000/api/health
```

Frontend:

```bash
cd frontend
npm install
npm run build
npx vite --port 5173
```

Existing API checks:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"verify\",\"message\":\"Find 2 papers about agent memory\"}"

curl http://localhost:8000/api/library/papers
curl http://localhost:8000/api/traces
curl http://localhost:8000/api/settings/preferences
curl http://localhost:8000/api/subscriptions
```

Agent scenario checks:

```text
1. Search returns paper cards and trace_id.
2. Follow-up "second paper" resolves previous result.
3. Deep-read creates or reuses local paper, parses PDF, and returns report.
4. Compare returns a structured comparison.
5. Literature survey returns synthesized findings.
6. Interest recommendation uses preferences or semantic history.
7. Preference update modifies SQL structured memory.
8. Trace diagnosis reads trace data and explains failures.
```

Trace checks:

```text
1. Every new Agent task returns trace_id.
2. /api/traces shows the task.
3. /api/traces/{trace_id} shows projected timeline steps.
4. Query rewrite and selected_skill are visible in input/output summaries or reasoning summary.
```

Guard checks:

```text
1. ReAct cannot call subscription_create.
2. ReAct cannot call notification sending.
3. Search-only requests cannot trigger paper_parse_full_text.
4. Expensive tools are not called without explicit user intent.
```

Claude Code final response must include:

```text
Completed content
Modified files
How to run
How to verify
Verification results
Known limitations or blockers
```

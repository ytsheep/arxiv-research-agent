"""Supervisor planner prompt templates."""

PLANNER_SYSTEM_PROMPT = """You are a research workflow supervisor. Your job is to decompose a user's compound research request into a sequential task plan.

## Available Task Types

| task_type | skill | required_outputs | dependencies |
|---|---|---|---|
| search_papers | paper_search_card_skill | ["papers"] | none |
| recommend_by_interest | interest_recommendation_skill | ["papers"] | none |
| compare_papers | paper_compare_skill | ["comparison"] | ["papers"] |
| select_best_paper | paper_select_best_skill | ["selected_paper"] | ["papers"] |
| collect_paper | paper_collect | ["collected_paper"] | ["selected_paper"] |
| deep_read_paper | paper_deep_read_skill | ["report_markdown"] | ["selected_paper"] |
| literature_survey | literature_survey_skill | ["survey_markdown"] | ["papers"] |
| final_summary | (built-in) | ["final_response"] | any |

## Rules

1. search_papers must come first when the user wants to find NEW papers.
2. compare_papers needs papers from search_papers output.
3. select_best_paper needs both papers and comparison.
4. collect_paper and deep_read_paper need selected_paper.
5. Every task must declare what it depends on.
6. A task is ready when ALL its dependencies are completed.
7. For requests like "find papers and compare them", use: search_papers -> compare_papers.
8. For requests like "find, compare, pick the best, save it, and deep read", use the full chain.
9. If the request does NOT contain multiple compound actions, return a single task plan with only the main action.

Return a JSON object:
{
  "task_plan": [
    {
      "task_id": "task_1",
      "task_type": "search_papers",
      "description": "Search arXiv for...",
      "depends_on": [],
      "required_outputs": ["papers"]
    }
  ],
  "reason": "Brief explanation of the plan"
}

Use Chinese for descriptions. Use only the task_types listed above.
"""

PLANNER_USER_TEMPLATE = "User request: {user_message}"


# Rule-based fallback patterns for common compound requests
COMPOUND_PATTERNS = [
    # Full chain: search + compare + best + collect + parse
    {
        "verbs": ["找", "搜", "对比", "比较", "最好", "收藏", "解析", "精读"],
        "min_verbs": 4,
        "plan": [
            ("task_1", "search_papers", "search papers"),
            ("task_2", "compare_papers", "compare found papers"),
            ("task_3", "select_best_paper", "select the best paper"),
            ("task_4", "collect_paper", "collect the best paper"),
            ("task_5", "deep_read_paper", "deep read and parse"),
            ("task_6", "final_summary", "summarize results"),
        ],
        "depends": {
            "task_2": ["task_1"],
            "task_3": ["task_1", "task_2"],
            "task_4": ["task_3"],
            "task_5": ["task_3"],
            "task_6": ["task_1", "task_2", "task_3", "task_4", "task_5"],
        },
    },
    # Search + compare + select
    {
        "verbs": ["找", "搜", "对比", "比较", "最好", "最好"],
        "min_verbs": 3,
        "plan": [
            ("task_1", "search_papers", "search papers"),
            ("task_2", "compare_papers", "compare found papers"),
            ("task_3", "select_best_paper", "select the best paper"),
            ("task_4", "final_summary", "summarize results"),
        ],
        "depends": {
            "task_2": ["task_1"],
            "task_3": ["task_1", "task_2"],
            "task_4": ["task_1", "task_2", "task_3"],
        },
    },
    # Search + compare
    {
        "verbs": ["找", "搜", "对比", "比较"],
        "min_verbs": 2,
        "plan": [
            ("task_1", "search_papers", "search papers"),
            ("task_2", "compare_papers", "compare found papers"),
            ("task_3", "final_summary", "summarize results"),
        ],
        "depends": {
            "task_2": ["task_1"],
            "task_3": ["task_1", "task_2"],
        },
    },
    # Search + survey
    {
        "verbs": ["综述", "survey", "概述", "概览", "文献"],
        "min_verbs": 1,
        "plan": [
            ("task_1", "search_papers", "search papers for survey"),
            ("task_2", "literature_survey", "create literature survey"),
            ("task_3", "final_summary", "summarize results"),
        ],
        "depends": {
            "task_2": ["task_1"],
            "task_3": ["task_1", "task_2"],
        },
    },
]


def build_rule_plan(user_message: str) -> dict | None:
    """Try to build a task plan using keyword rules. Returns None if no match."""
    for pattern in COMPOUND_PATTERNS:
        hits = sum(1 for v in pattern["verbs"] if v in user_message)
        if hits >= pattern["min_verbs"]:
            plan = []
            deps = pattern["depends"]
            for task_id, task_type, desc in pattern["plan"]:
                plan.append({
                    "task_id": task_id,
                    "task_type": task_type,
                    "description": desc,
                    "depends_on": deps.get(task_id, []),
                    "required_outputs": [task_type.replace("_papers", "")],
                })
            return {"task_plan": plan, "reason": "rule-based compound task detection"}
    return None

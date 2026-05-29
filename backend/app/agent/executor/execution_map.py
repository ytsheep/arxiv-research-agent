"""Deterministic task_type -> (skill_name, arg_mapping) routing table.

The Executor uses this table directly. No LLM reasoning, no free-form ReAct.
"""

# Each entry maps a task_type to (skill_name, arg_mapping_dict)
# arg_mapping values can be:
#   - a state field name (e.g. "user_message" -> reads state["user_message"])
#   - a dotted path (e.g. "selected_paper.arxiv_id" -> reads from task_outputs)
#   - a literal string (prefixed with "literal:")

EXECUTION_MAP = {
    "search_papers": ("paper_search_card_skill", {
        "user_message": "user_message",
        "topic": "topic",
        "top_n": "top_n",
        "candidate_k": "candidate_k",
    }),
    "recommend_by_interest": ("interest_recommendation_skill", {
        "user_message": "user_message",
        "top_n": "top_n",
        "candidate_k": "candidate_k",
    }),
    "compare_papers": ("paper_compare_skill", {
        "papers": "papers",
        "arxiv_ids": "arxiv_ids",
        "user_message": "user_message",
    }),
    "select_best_paper": ("paper_select_best_skill", {
        "papers": "papers",
        "comparison": "comparison",
        "user_message": "user_message",
    }),
    "collect_paper": ("paper_collect", {
        "paper": "selected_paper",
    }),
    "deep_read_paper": ("paper_deep_read_skill", {
        "arxiv_id": "selected_paper.arxiv_id",
        "user_message": "user_message",
    }),
    "literature_survey": ("literature_survey_skill", {
        "user_message": "user_message",
        "topic": "topic",
        "top_n": "top_n",
    }),
    "library_search": ("library_search_papers", {
        "keyword": "keyword",
    }),
    "trace_diagnosis": ("trace_diagnosis_skill", {
        "user_message": "user_message",
    }),
    "memory_profile": ("memory_profile_skill", {
        "user_message": "user_message",
    }),
    "final_summary": ("_final_summary", {}),
}

# Required outputs per task_type for completion checking
REQUIRED_OUTPUTS_MAP = {
    "search_papers": ["papers"],
    "recommend_by_interest": ["papers"],
    "compare_papers": ["comparison"],
    "select_best_paper": ["selected_paper"],
    "collect_paper": ["collected_paper"],
    "deep_read_paper": ["report_markdown"],
    "literature_survey": ["survey_markdown"],
    "library_search": ["papers"],
    "trace_diagnosis": ["diagnosis"],
    "memory_profile": ["preferences"],
    "final_summary": [],
}

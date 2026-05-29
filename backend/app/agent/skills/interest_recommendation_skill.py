"""Interest Recommendation Skill: use preferences + semantic memory to recommend papers."""

from app.agent.skills.paper_search_card_skill import paper_search_card_skill
from app.services.memory_service import SemanticMemoryService
from app.tools.trace_tool import TraceTool
from app.core.logging import logger

INTEREST_RECOMMENDATION_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "interest_recommendation_skill",
        "description": "Recommend papers based on user's long-term research interests and semantic memory. Use this when the user asks for papers based on their interests or preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "The original user message",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of papers to recommend (default 2)",
                    "default": 2,
                },
                "candidate_k": {
                    "type": "integer",
                    "description": "Number of candidate papers to fetch (default 20)",
                    "default": 20,
                },
            },
            "required": ["user_message"],
        },
    },
}


async def interest_recommendation_skill(
    user_message: str = "",
    top_n: int = 2,
    candidate_k: int = 20,
) -> dict:
    trace_tool = TraceTool()
    semantic_memory = SemanticMemoryService()

    trace = trace_tool.create(task_type="interest_recommendation", user_input=user_message)
    logger.info(f"[Skill:interest_recommendation trace={trace.trace_id}] top_n={top_n}")

    # Step 1: Load preferences
    preferences = await semantic_memory.load_user_preferences()
    preferred_topics = preferences.get("preferred_topics", [])
    preferred_categories = preferences.get("preferred_categories", [])
    topic_weights = preferences.get("topic_interest_weights", {})

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="load_user_preferences",
        input_summary="",
        output_summary=f"topics={preferred_topics[:6]}, categories={preferred_categories[:6]}",
    )

    # Step 2: Generate query from preferences
    if preferred_topics:
        search_query = " ".join(preferred_topics[:5])
    elif topic_weights:
        sorted_topics = sorted(topic_weights, key=topic_weights.get, reverse=True)
        search_query = " ".join(sorted_topics[:5])
    else:
        search_query = "machine learning artificial intelligence"

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="query_rewrite",
        input_summary=f"topics={preferred_topics[:6]}, weights={list(topic_weights.keys())[:6]}",
        output_summary=f"search_query={search_query}",
    )

    # Step 3: Search papers
    search_result = await paper_search_card_skill(
        user_message=user_message,
        topic=search_query,
        top_n=top_n,
        candidate_k=min(candidate_k, 50),
    )
    papers = search_result.get("papers", [])
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="arxiv_search",
        input_summary=f"query={search_query}, top_n={top_n}",
        output_summary=f"found={len(papers)} papers",
    )

    # Build interest-based message
    if not papers:
        await trace_tool.complete(trace.trace_id, status="success", trace=trace)
        return {
            "success": True,
            "trace_id": trace.trace_id,
            "message": f'你的兴趣方向: {", ".join(preferred_topics[:5])}。当前未找到新论文。',
            "papers": [],
        }

    interest_msg = f'基于你的兴趣 ({", ".join(preferred_topics[:4]) if preferred_topics else "AI/ML"})，为你推荐 {len(papers)} 篇论文'

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="generate_recommendations",
        input_summary=f"papers={len(papers)}",
        output_summary=interest_msg,
    )

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "message": interest_msg,
        "papers": papers,
    }

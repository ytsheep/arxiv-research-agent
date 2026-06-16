"""Input Resolver: resolves executor arguments from task_outputs and state."""

from app.core.logging import logger


class InputResolver:
    """Resolves executor input arguments by reading from task_outputs and state.

    Supports dotted paths like "selected_paper.arxiv_id" to drill into
    previous task outputs.
    """

    @staticmethod
    def resolve(
        arg_mapping: dict,
        task_outputs: dict[str, dict],
        user_message: str = "",
        user_preferences: dict | None = None,
        default_top_n: int = 2,
        default_candidate_k: int = 20,
    ) -> dict:
        resolved = {}
        for arg_name, arg_source in arg_mapping.items():
            if not arg_source:
                continue
            value = InputResolver._resolve_source(
                arg_source, task_outputs, user_message,
                user_preferences or {}, default_top_n, default_candidate_k,
            )
            if value is not None:
                resolved[arg_name] = value

        if "user_message" not in resolved and user_message:
            resolved["user_message"] = user_message
        return resolved

    @staticmethod
    def _resolve_source(
        source: str,
        task_outputs: dict[str, dict],
        user_message: str,
        user_preferences: dict,
        default_top_n: int,
        default_candidate_k: int,
    ):
        if source == "user_message":
            return user_message
        if source == "topic":
            return InputResolver._extract_topic(user_message, user_preferences)
        if source == "top_n":
            return default_top_n
        if source == "candidate_k":
            return default_candidate_k

        # Dotted path: "selected_paper.arxiv_id" -> find "selected_paper" in task_outputs, then drill
        if "." in source:
            parts = source.split(".", 1)
            primary_key = parts[0]
            sub_path = parts[1]
            for output in task_outputs.values():
                if primary_key in output:
                    nested = output[primary_key]
                    if isinstance(nested, dict):
                        return nested.get(sub_path)
                    return nested
            # Try direct lookup from any task output field
            for output in task_outputs.values():
                if isinstance(output, dict) and primary_key in output:
                    return output[primary_key]
            return None

        # Simple field name: look up in task_outputs
        for output in task_outputs.values():
            if isinstance(output, dict) and source in output and output[source] is not None:
                val = output[source]
                if isinstance(val, list):
                    return val
                if isinstance(val, dict) and val:
                    return val
                if val:
                    return val
        return None

    @staticmethod
    def _extract_topic(user_message: str, preferences: dict) -> str:
        """Extract topic from user message or fall back to preferences."""
        import re
        # Try to extract topic after Chinese prefixes
        patterns = [
            r"关于\s*(\S+?)(?:\s*(?:的|论文|方向|领域|研究))",
            r"(?:找|搜索|搜|检索|推荐)\s*(?:\d+|[一二三四五六七八九十两几]+)?\s*篇?\s*(?:关于|有关)?\s*(.+?)\s*(?:相关)?(?:的)?论文",
        ]
        for pat in patterns:
            m = re.search(pat, user_message)
            if m:
                topic = m.group(1).strip(" ,.;:，。")
                if topic:
                    return topic

        prefs = preferences or {}
        topics = prefs.get("preferred_topics", [])
        if topics:
            return " ".join(topics[:3])
        return "machine learning artificial intelligence"

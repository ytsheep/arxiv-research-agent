from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime
from typing import Any

from sqlalchemy import desc, or_, select

from app.core.config import settings
from app.db.database import async_session
from app.models.memory import ChatMessage, SemanticMemory
from app.models.settings import UserPreference
from app.tools.embedding_tool import cosine_similarity
from app.tools.llm_client import llm_client


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def _json_loads(raw: str | None, default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9\u4e00-\u9fff][A-Za-z0-9_\-\u4e00-\u9fff]*", text.lower())
    return [token for token in tokens if len(token) > 1]


def _tfidf_scores(query: str, documents: list[str]) -> list[float]:
    query_tokens = _tokenize(query)
    doc_tokens = [_tokenize(doc) for doc in documents]
    vocab = sorted(set(query_tokens).union(*(set(tokens) for tokens in doc_tokens)))
    if not vocab:
        return [0.0 for _ in documents]

    n_docs = max(1, len(documents))
    idf = {}
    for term in vocab:
        doc_count = sum(1 for tokens in doc_tokens if term in tokens)
        idf[term] = math.log((n_docs + 1) / (doc_count + 1)) + 1.0

    def vector(tokens: list[str]) -> list[float]:
        counts = Counter(tokens)
        vec = [counts.get(term, 0) * idf.get(term, 1.0) for term in vocab]
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec] if norm else vec

    query_vec = vector(query_tokens)
    return [cosine_similarity(query_vec, vector(tokens)) for tokens in doc_tokens]


class ShortTermMemoryService:
    """Session-scoped Messages List with tool-call/tool-response pair truncation."""

    async def add_user_message(self, session_id: str, content: str, metadata: dict | None = None) -> None:
        await self._add_message(session_id, "user", content, "chat", metadata=metadata)

    async def add_assistant_message(self, session_id: str, content: str, metadata: dict | None = None) -> None:
        await self._add_message(session_id, "assistant", content, "chat", metadata=metadata)

    async def add_tool_call(
        self,
        session_id: str,
        group_id: str,
        tool_call_id: str,
        tool_name: str,
        arguments: dict,
    ) -> None:
        content = f"tool_call name={tool_name} arguments={_json_dumps(arguments)}"
        await self._add_message(
            session_id=session_id,
            role="assistant",
            content=content,
            message_type="tool_call",
            metadata={"arguments": arguments},
            group_id=group_id,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
        )

    async def add_tool_response(
        self,
        session_id: str,
        group_id: str,
        tool_call_id: str,
        tool_name: str,
        response: dict,
    ) -> None:
        response_summary = self._summarize_tool_response(response)
        await self._add_message(
            session_id=session_id,
            role="tool",
            content=response_summary,
            message_type="tool_response",
            metadata={"response": response},
            group_id=group_id,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
        )

    async def load_messages(
        self,
        session_id: str,
        token_budget: int = 3500,
        max_rows: int = 80,
    ) -> list[dict[str, str]]:
        rows = await self._recent_rows(session_id, max_rows=max_rows)
        units = self._group_rows(rows)
        kept: list[dict[str, str]] = []
        used = 0

        for unit in reversed(units):
            token_cost = unit["token_estimate"]
            if used + token_cost <= token_budget:
                kept.append(unit["message"])
                used += token_cost
                continue

            compact = self._compact_unit(unit)
            compact_cost = _estimate_tokens(compact["content"])
            if used + compact_cost <= token_budget:
                kept.append(compact)
                used += compact_cost

        kept.reverse()
        return kept

    async def build_context_summary(self, session_id: str, token_budget: int = 1200) -> str:
        messages = await self.load_messages(session_id, token_budget=token_budget)
        lines = []
        for msg in messages:
            role = msg.get("role", "message")
            content = msg.get("content", "").strip().replace("\n", " ")
            if content:
                lines.append(f"{role}: {content[:500]}")
        return "\n".join(lines)

    async def get_last_papers(self, session_id: str) -> list[dict[str, Any]]:
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id, ChatMessage.role == "assistant")
                .order_by(desc(ChatMessage.id))
                .limit(30)
            )
            rows = result.scalars().all()

        for row in rows:
            metadata = _json_loads(row.metadata_json, {})
            papers = metadata.get("papers", [])
            if papers:
                return papers
        return []

    async def _add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str,
        metadata: dict | None = None,
        group_id: str | None = None,
        tool_call_id: str | None = None,
        tool_name: str | None = None,
    ) -> None:
        async with async_session() as session:
            session.add(ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                message_type=message_type,
                group_id=group_id,
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                metadata_json=_json_dumps(metadata or {}),
                token_estimate=_estimate_tokens(content),
                created_at=_now(),
            ))
            await session.commit()

    async def _recent_rows(self, session_id: str, max_rows: int) -> list[ChatMessage]:
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.id))
                .limit(max_rows)
            )
            rows = result.scalars().all()
        return list(reversed(rows))

    def _group_rows(self, rows: list[ChatMessage]) -> list[dict[str, Any]]:
        units: list[dict[str, Any]] = []
        index = 0
        while index < len(rows):
            row = rows[index]
            if row.message_type in {"tool_call", "tool_response"} and row.group_id:
                group = [row]
                index += 1
                while index < len(rows) and rows[index].group_id == row.group_id:
                    group.append(rows[index])
                    index += 1
                content = self._summarize_tool_group(group)
                units.append({
                    "rows": group,
                    "message": {"role": "assistant", "content": content},
                    "token_estimate": _estimate_tokens(content),
                    "is_tool_group": True,
                })
                continue

            units.append({
                "rows": [row],
                "message": {"role": row.role if row.role in {"user", "assistant"} else "assistant", "content": row.content},
                "token_estimate": row.token_estimate or _estimate_tokens(row.content),
                "is_tool_group": False,
            })
            index += 1
        return units

    def _compact_unit(self, unit: dict[str, Any]) -> dict[str, str]:
        if unit.get("is_tool_group"):
            rows = unit["rows"]
            tool_name = rows[0].tool_name or "tool"
            return {"role": "assistant", "content": f"Earlier paired tool interaction: {tool_name} executed; result is summarized."}
        content = unit["message"]["content"]
        return {"role": unit["message"]["role"], "content": content[:300]}

    def _summarize_tool_group(self, rows: list[ChatMessage]) -> str:
        tool_name = rows[0].tool_name or "tool"
        call = next((row for row in rows if row.message_type == "tool_call"), None)
        response = next((row for row in rows if row.message_type == "tool_response"), None)
        call_meta = _json_loads(call.metadata_json if call else "", {})
        response_meta = _json_loads(response.metadata_json if response else "", {})
        args = call_meta.get("arguments", {})
        output = self._summarize_tool_response(response_meta.get("response", {})) if response else "missing response"
        return f"Paired tool interaction: {tool_name} args={_json_dumps(args)}; response={output}"

    def _summarize_tool_response(self, response: dict) -> str:
        if not response:
            return "empty response"
        if response.get("papers"):
            return f"success={response.get('success', True)}, papers={len(response.get('papers', []))}"
        if response.get("ranked_papers"):
            return f"success={response.get('success', True)}, ranked_papers={len(response.get('ranked_papers', []))}"
        if response.get("error"):
            return f"success={response.get('success', False)}, error={response.get('error')}"
        return str({k: response.get(k) for k in list(response.keys())[:6]})[:800]


class SemanticMemoryService:
    """Long-term semantic memory backed by SQLite-stored embeddings."""

    async def load_user_preferences(self) -> dict[str, Any]:
        async with async_session() as session:
            result = await session.execute(select(UserPreference))
            rows = result.scalars().all()
        prefs = {row.key: row.value for row in rows}
        return {
            "preferred_categories": self._split_pref(prefs.get("preferred_categories", "")),
            "preferred_topics": self._split_pref(prefs.get("preferred_topics", "")),
            "topic_interest_weights": _json_loads(prefs.get("topic_interest_weights"), {}),
        }

    async def infer_interest_query(self, session_id: str, fallback: str = "machine learning") -> str:
        prefs = await self.load_user_preferences()
        topics = prefs.get("preferred_topics") or []
        if topics:
            return " ".join(topics[:5])

        memories = await self.retrieve(
            query="paper search research interests preferences",
            session_id=session_id,
            top_k=5,
            source_types=["search_history", "paper"],
        )
        extracted: list[str] = []
        for memory in memories:
            extracted.extend(_tokenize(memory.get("title", "") + " " + memory.get("content", ""))[:4])
        extracted = self._rank_terms(extracted)
        return " ".join(extracted[:5]) if extracted else fallback

    async def retrieve(
        self,
        query: str,
        session_id: str = "",
        top_k: int = 5,
        source_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        async with async_session() as session:
            stmt = select(SemanticMemory).where(
                or_(
                    SemanticMemory.session_id == session_id,
                    SemanticMemory.session_id == "",
                    SemanticMemory.session_id.is_(None),
                )
            )
            if source_types:
                stmt = stmt.where(SemanticMemory.source_type.in_(source_types))
            result = await session.execute(stmt.order_by(desc(SemanticMemory.id)).limit(200))
            rows = result.scalars().all()

        if not rows:
            return []

        scored = await self._score_memories(query, rows)
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    async def remember_search(
        self,
        session_id: str,
        trace_id: str,
        query: str,
        user_message: str,
        papers: list[dict[str, Any]],
    ) -> None:
        if query:
            await self.update_topic_preferences(query)

        paper_titles = "; ".join(p.get("title", "") for p in papers[:5] if p.get("title"))
        await self.upsert_memory(
            session_id=session_id,
            source_type="search_history",
            source_id=f"trace:{trace_id}",
            title=f"Search: {query}",
            content=f"User message: {user_message}\nSearch query: {query}\nSelected papers: {paper_titles}",
            metadata={"trace_id": trace_id, "query": query, "paper_count": len(papers)},
            importance=0.7,
        )

        for paper in papers:
            await self.remember_paper(paper)

    async def remember_paper(self, paper: dict[str, Any]) -> None:
        arxiv_id = paper.get("arxiv_id", "")
        if not arxiv_id:
            return
        title = paper.get("title", "")
        abstract = paper.get("abstract", "") or paper.get("summary", "")
        categories = paper.get("categories", [])
        content = f"{title}\n{abstract}\nCategories: {', '.join(categories) if isinstance(categories, list) else categories}"
        await self.upsert_memory(
            session_id="",
            source_type="paper",
            source_id=f"paper:{arxiv_id}",
            title=title,
            content=content,
            metadata={"arxiv_id": arxiv_id, "categories": categories},
            importance=0.8,
        )

    async def remember_report(self, arxiv_id: str, report_markdown: str) -> None:
        chunks = self._split_markdown(report_markdown)
        for index, chunk in enumerate(chunks[:12]):
            await self.upsert_memory(
                session_id="",
                source_type="report",
                source_id=f"report:{arxiv_id}:{index}",
                title=chunk["title"],
                content=chunk["content"],
                metadata={"arxiv_id": arxiv_id, "chunk_index": index},
                importance=0.9,
            )

    async def update_topic_preferences(self, query: str) -> None:
        terms = self._extract_topic_terms(query)
        if not terms:
            return

        async with async_session() as session:
            result = await session.execute(
                select(UserPreference).where(UserPreference.key == "topic_interest_weights")
            )
            row = result.scalar_one_or_none()
            weights = _json_loads(row.value if row else "", {})
            for term in terms:
                weights[term] = float(weights.get(term, 0.0)) + 1.0
            top_terms = sorted(weights, key=weights.get, reverse=True)[:12]
            now = _now()

            if row:
                row.value = _json_dumps(weights)
                row.updated_at = now
            else:
                session.add(UserPreference(
                    key="topic_interest_weights",
                    value=_json_dumps(weights),
                    updated_at=now,
                ))

            pref_result = await session.execute(
                select(UserPreference).where(UserPreference.key == "preferred_topics")
            )
            pref_row = pref_result.scalar_one_or_none()
            pref_value = ", ".join(top_terms[:8])
            if pref_row:
                pref_row.value = pref_value
                pref_row.updated_at = now
            else:
                session.add(UserPreference(key="preferred_topics", value=pref_value, updated_at=now))

            await session.commit()

    async def upsert_memory(
        self,
        session_id: str,
        source_type: str,
        source_id: str,
        title: str,
        content: str,
        metadata: dict | None = None,
        importance: float = 0.5,
    ) -> None:
        embedding = await self._embed(content)
        async with async_session() as session:
            result = await session.execute(
                select(SemanticMemory).where(
                    SemanticMemory.source_type == source_type,
                    SemanticMemory.source_id == source_id,
                )
            )
            row = result.scalar_one_or_none()
            now = _now()
            if row:
                row.session_id = session_id
                row.title = title
                row.content = content[:12000]
                row.metadata_json = _json_dumps(metadata or {})
                row.embedding_json = _json_dumps(embedding) if embedding else ""
                row.importance = importance
                row.updated_at = now
            else:
                session.add(SemanticMemory(
                    session_id=session_id,
                    source_type=source_type,
                    source_id=source_id,
                    title=title,
                    content=content[:12000],
                    metadata_json=_json_dumps(metadata or {}),
                    embedding_json=_json_dumps(embedding) if embedding else "",
                    importance=importance,
                    created_at=now,
                    updated_at=now,
                ))
            await session.commit()

    async def _score_memories(self, query: str, rows: list[SemanticMemory]) -> list[dict[str, Any]]:
        query_embedding = await self._embed(query)
        use_embedding = bool(query_embedding) and all(row.embedding_json for row in rows)
        if use_embedding:
            scores = [
                cosine_similarity(query_embedding, _json_loads(row.embedding_json, []))
                for row in rows
            ]
        else:
            scores = _tfidf_scores(query, [f"{row.title or ''}\n{row.content or ''}" for row in rows])

        result = []
        for row, score in zip(rows, scores):
            metadata = _json_loads(row.metadata_json, {})
            final_score = float(score) + 0.05 * float(row.importance or 0.0)
            result.append({
                "source_type": row.source_type,
                "source_id": row.source_id,
                "title": row.title or "",
                "content": row.content,
                "metadata": metadata,
                "score": round(final_score, 4),
            })
        return result

    async def _embed(self, text: str) -> list[float]:
        if not text:
            return []
        from app.tools.local_embedding import embed_single
        return embed_single(text[:8000])

    def _extract_topic_terms(self, query: str) -> list[str]:
        stop_words = {
            "paper", "papers", "about", "find", "search", "recommend", "please",
            "give", "me", "the", "a", "an", "and", "or", "of", "for", "with",
            "two", "three", "one", "some", "related",
        }
        return [term for term in _tokenize(query) if term not in stop_words and not term.isdigit()][:10]

    def _rank_terms(self, terms: list[str]) -> list[str]:
        counts = Counter(term for term in terms if len(term) > 1)
        return [term for term, _ in counts.most_common()]

    def _split_pref(self, raw: str) -> list[str]:
        return [item.strip() for item in raw.split(",") if item.strip()]

    def _split_markdown(self, markdown: str) -> list[dict[str, str]]:
        chunks = []
        current_title = "Report"
        current_lines: list[str] = []
        for line in markdown.splitlines():
            if line.startswith("#"):
                if current_lines:
                    chunks.append({"title": current_title, "content": "\n".join(current_lines).strip()})
                    current_lines = []
                current_title = line.lstrip("#").strip() or "Report"
            else:
                current_lines.append(line)
        if current_lines:
            chunks.append({"title": current_title, "content": "\n".join(current_lines).strip()})
        return [chunk for chunk in chunks if chunk["content"]]

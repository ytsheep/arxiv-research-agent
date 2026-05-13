"""Rerank tool: scores and ranks candidate papers with semantic and keyword signals."""

from __future__ import annotations
import re
from app.core.logging import logger
from app.tools.embedding_tool import EmbeddingTool


class RerankTool:
    def __init__(self):
        self.embedding_tool = EmbeddingTool()

    async def rerank(
        self,
        query: str,
        papers: list[dict],
        top_n: int = 2,
        user_preferences: dict | None = None,
    ) -> dict:
        """Rerank candidate papers and return top N. Uses semantic embeddings + keyword + recency."""
        if not papers:
            return {"success": True, "ranked_papers": []}

        # Get semantic similarity scores via embedding
        semantic_scores, semantic_method = await self._semantic_scores(query, papers)

        query_lower = query.lower()
        query_keywords = self._extract_keywords(query)

        scored = []
        for i, paper in enumerate(papers):
            title = paper.get("title", "")
            abstract = paper.get("abstract", "")
            categories = paper.get("categories", [])
            published_date = paper.get("published_date", "")

            title_lower = title.lower()
            abstract_lower = abstract.lower()

            # Semantic score (from embeddings or TF-IDF)
            semantic_score = semantic_scores[i] if i < len(semantic_scores) else 0.5

            # Keyword match score (complementary)
            keyword_score = self._keyword_match_score(query_keywords, title_lower, abstract_lower)

            # Recency score
            recency_score = self._recency_score(published_date)

            # Category preference score
            pref_score = 0.5
            if user_preferences:
                pref_cats = user_preferences.get("preferred_categories", [])
                if pref_cats:
                    matched_cats = set(categories) & set(pref_cats)
                    pref_score = min(1.0, 0.5 + len(matched_cats) * 0.25)

            # Combined score: semantic primary, keyword/recency secondary
            final_score = (
                0.45 * semantic_score
                + 0.20 * keyword_score
                + 0.15 * recency_score
                + 0.10 * pref_score
                + 0.10 * (semantic_score * recency_score)  # interaction term
            )

            scored.append({
                **paper,
                "final_score": round(final_score, 3),
                "semantic_score": round(semantic_score, 3),
                "keyword_match_score": round(keyword_score, 3),
                "recency_score": round(recency_score, 3),
                "user_preference_score": round(pref_score, 3),
            })

        scored.sort(key=lambda p: p["final_score"], reverse=True)
        top_papers = scored[:top_n]

        # Generate basic summaries (may be overwritten by LLM later)
        for paper in top_papers:
            paper["summary"] = self._simple_summary(paper)
            paper["core_problem"] = self._extract_core_problem(paper)
            paper["method"] = self._extract_method_hint(paper)
            paper["result"] = self._extract_result_hint(paper)
            paper["summary_source"] = "metadata_only"

        logger.info(
            f"Rerank: {len(papers)} candidates → top {len(top_papers)} "
            f"(semantic={semantic_method})"
        )
        return {"success": True, "ranked_papers": top_papers}

    async def _semantic_scores(self, query: str, papers: list[dict]) -> tuple[list[float], str]:
        """Get semantic similarity scores for each paper against the query.
        Returns (scores, method_used)."""
        try:
            ranked, method = await self.embedding_tool.rank_by_similarity(
                query=query,
                papers=papers,
                top_n=len(papers),
            )
            score_map = {}
            for p in ranked:
                aid = p.get("arxiv_id", "")
                score_map[aid] = p.get("_rerank_score", 0.5)

            scores = []
            for paper in papers:
                aid = paper.get("arxiv_id", "")
                scores.append(score_map.get(aid, 0.5))
            return scores, method
        except Exception as e:
            logger.warning(f"Semantic scoring failed, using keyword fallback: {e}")
            query_keywords = self._extract_keywords(query)
            return [
                self._keyword_match_score(
                    query_keywords,
                    paper.get("title", "").lower(),
                    paper.get("abstract", "").lower(),
                )
                for paper in papers
            ], "keyword"

    def _extract_keywords(self, query: str) -> list[str]:
        stop_words = {
            "about", "on", "in", "for", "of", "the", "a", "an", "is", "are",
            "论文", "的", "关于", "给我", "找", "篇", "一些", "推荐", "搜索",
        }
        words = re.findall(r"\w+", query.lower())
        return [w for w in words if w not in stop_words and len(w) > 1]

    def _keyword_match_score(self, keywords: list[str], title: str, abstract: str) -> float:
        if not keywords:
            return 0.5
        text = title + " " + abstract
        matches = sum(1 for kw in keywords if kw.lower() in text)
        return min(1.0, matches / max(len(keywords), 1))

    def _recency_score(self, published_date: str) -> float:
        if not published_date:
            return 0.5
        import datetime as dt
        try:
            pub_date = dt.datetime.strptime(published_date, "%Y-%m-%d")
            days_ago = (dt.datetime.now() - pub_date).days
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.9
            elif days_ago <= 90:
                return 0.7
            elif days_ago <= 180:
                return 0.5
            elif days_ago <= 365:
                return 0.3
            else:
                return 0.1
        except (ValueError, TypeError):
            return 0.5

    def _simple_summary(self, paper: dict) -> str:
        abstract = paper.get("abstract", "")
        sentences = re.split(r"[.。!！?？]\s+", abstract)
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        return "。".join(s for s in summary_sentences if s.strip()) + "。"

    def _extract_core_problem(self, paper: dict) -> str:
        abstract = paper.get("abstract", "")
        patterns = [
            r"(?:challenge|problem|issue|limitation|瓶颈|挑战|问题|不足|局限)(?:\s+is|\s+are|：|:)?\s*(.+?)(?:[.。]|$)",
            r"(?:However|But|Unfortunately|然而|但是)(?:,)?\s*(.+?)(?:[.。]|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        return "详见论文摘要"

    def _extract_method_hint(self, paper: dict) -> str:
        abstract = paper.get("abstract", "")
        patterns = [
            r"(?:propose|present|introduce|develop|提出|提出了一种|介绍了|设计)(?:\s+a|\s+an)?\s*(.+?)(?:[.。]|$)",
            r"(?:approach|method|framework|方法|框架|架构)(?:\s+is|\s+are|：|:)?\s*(.+?)(?:[.。]|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        return "详见论文"

    def _extract_result_hint(self, paper: dict) -> str:
        abstract = paper.get("abstract", "")
        patterns = [
            r"(?:result|finding|show|demonstrate|achieve|实验|结果|表明|显示|证明)(?:\s+that)?\s*(.+?)(?:[.。]|$)",
            r"(?:outperform|improve|提升|超过|优于)(?:\s+by)?\s*(.+?)(?:[.。]|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        return "详见论文"

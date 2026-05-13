"""arXiv API tool: search papers via arXiv API."""

import httpx
import xml.etree.ElementTree as ET
from app.core.logging import logger

ARXIV_API_BASE = "https://export.arxiv.org/api/query"


class ArxivTool:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client

    async def search(
        self,
        query: str,
        max_results: int = 20,
        categories: list[str] | None = None,
        sort_by: str = "relevance",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict:
        """Search arXiv for papers matching the query."""
        # Build search query with categories
        search_query_parts = [query]

        if categories:
            cat_query = " OR ".join(f"cat:{c}" for c in categories)
            search_query_parts.append(f"({cat_query})")

        search_query = " AND ".join(f"({p})" for p in search_query_parts)

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max_results, 50),
            "sortBy": sort_by,
        }

        try:
            client = await self._get_client()
            response = await client.get(ARXIV_API_BASE, params=params)
            response.raise_for_status()

            papers = self._parse_atom(response.text)
            logger.info(f"arXiv search returned {len(papers)} papers for query: {query[:80]}")

            return {"success": True, "papers": papers, "error": None}

        except httpx.HTTPError as e:
            logger.error(f"arXiv API request failed: {e}")
            return {"success": False, "papers": [], "error": f"arXiv API 请求失败: {str(e)}"}
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return {"success": False, "papers": [], "error": f"arXiv 检索失败: {str(e)}"}

    def _parse_atom(self, xml_text: str) -> list[dict]:
        """Parse arXiv Atom XML response into paper dicts."""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        root = ET.fromstring(xml_text)
        papers = []

        for entry in root.findall("atom:entry", ns):
            try:
                paper = self._parse_entry(entry, ns)
                papers.append(paper)
            except Exception as e:
                logger.warning(f"Failed to parse arXiv entry: {e}")

        return papers

    def _parse_entry(self, entry, ns) -> dict:
        """Parse a single arXiv Atom entry."""
        title_el = entry.find("atom:title", ns)
        title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""

        # Get arXiv ID from the id URL
        id_el = entry.find("atom:id", ns)
        arxiv_id = ""
        arxiv_url = ""
        if id_el is not None and id_el.text:
            arxiv_url = id_el.text.strip()
            arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else ""

        # PDF URL
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""

        # Authors
        authors = []
        for author_el in entry.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        # Summary (abstract)
        summary_el = entry.find("atom:summary", ns)
        abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else ""

        # Categories
        categories = []
        for cat_el in entry.findall("atom:category", ns):
            term = cat_el.get("term", "")
            if term:
                categories.append(term)

        # Published date
        published_el = entry.find("atom:published", ns)
        published_date = published_el.text.strip()[:10] if published_el is not None and published_el.text else ""

        # Updated date
        updated_el = entry.find("atom:updated", ns)
        updated_date = updated_el.text.strip()[:10] if updated_el is not None and updated_el.text else ""

        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "categories": categories,
            "published_date": published_date,
            "updated_date": updated_date,
            "arxiv_url": arxiv_url,
            "pdf_url": pdf_url,
        }

    async def get_paper_metadata(self, arxiv_id: str) -> dict:
        """Get metadata for a single paper by arXiv ID."""
        params = {
            "search_query": f"id:{arxiv_id}",
            "start": 0,
            "max_results": 1,
        }

        try:
            client = await self._get_client()
            response = await client.get(ARXIV_API_BASE, params=params)
            response.raise_for_status()

            papers = self._parse_atom(response.text)
            if papers:
                return {"success": True, "paper": papers[0], "error": None}
            return {"success": False, "paper": None, "error": "PAPER_NOT_FOUND"}

        except Exception as e:
            return {"success": False, "paper": None, "error": str(e)}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

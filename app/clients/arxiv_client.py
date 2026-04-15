import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List

from app.config import Settings
from app.models import Paper


class ArxivClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def search(self, search_query: str, max_results: int | None = None) -> List[Paper]:
        query = search_query.strip() or "cat:cs.AI"
        safe_query = urllib.parse.quote_plus(query, safe=':()"')
        max_items = max_results or 50
        url = (
            "http://export.arxiv.org/api/query"
            f"?search_query={safe_query}"
            "&sortBy=submittedDate"
            "&sortOrder=descending" 
            f"&max_results={max_items}"
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "arXiv-Research-Agent/1.0"},
        )

        with urllib.request.urlopen(
            request,
            timeout=self.settings.request_timeout_seconds,
        ) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        papers: List[Paper] = []
        for entry in root.findall("atom:entry", ns):
            entry_url = entry.findtext("atom:id", default="", namespaces=ns)
            paper_id = entry_url.split("/")[-1]
            title = entry.findtext("atom:title", default="", namespaces=ns).replace("\n", " ").strip()
            summary = entry.findtext("atom:summary", default="", namespaces=ns).replace("\n", " ").strip()
            published = entry.findtext("atom:published", default="", namespaces=ns)
            updated = entry.findtext("atom:updated", default="", namespaces=ns)
            authors = [
                author.findtext("atom:name", default="", namespaces=ns).strip()
                for author in entry.findall("atom:author", ns)
            ]

            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", "")
                    break
            if not pdf_url and entry_url:
                pdf_url = entry_url.replace("/abs/", "/pdf/") + ".pdf"

            papers.append(
                Paper(
                    id=paper_id,
                    title=title,
                    summary=summary,
                    entry_url=entry_url,
                    pdf_url=pdf_url,
                    published=published,
                    updated=updated,
                    authors=[author for author in authors if author],
                )
            )

        return papers

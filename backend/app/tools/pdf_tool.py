"""PDF tool: download and parse PDF files."""

import os
import re
import httpx
import fitz
from app.core.logging import logger
from app.storage.file_manager import FileManager


class PdfTool:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self.file_manager = FileManager()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        return self._client

    async def download_pdf(self, arxiv_id: str, pdf_url: str = "") -> dict:
        """Download PDF from arXiv to local storage."""
        target_dir = self.file_manager.ensure_paper_dir(arxiv_id)
        pdf_path = os.path.join(target_dir, "paper.pdf")

        if os.path.exists(pdf_path):
            logger.info(f"PDF already exists for {arxiv_id}")
            return {
                "success": True,
                "arxiv_id": arxiv_id,
                "pdf_path": pdf_path,
                "error": None,
            }

        url = pdf_url or f"https://arxiv.org/pdf/{arxiv_id}"
        try:
            client = await self._get_client()
            response = await client.get(url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "html" in content_type:
                return {
                    "success": False,
                    "arxiv_id": arxiv_id,
                    "pdf_path": "",
                    "error": f"arXiv returned HTML instead of PDF for {arxiv_id}",
                }

            with open(pdf_path, "wb") as f:
                f.write(response.content)

            file_size = os.path.getsize(pdf_path)
            logger.info(f"PDF downloaded for {arxiv_id}: {file_size} bytes")
            return {
                "success": True,
                "arxiv_id": arxiv_id,
                "pdf_path": pdf_path,
                "error": None,
            }

        except httpx.HTTPError as e:
            logger.error(f"PDF download failed for {arxiv_id}: {e}")
            return {
                "success": False,
                "arxiv_id": arxiv_id,
                "pdf_path": "",
                "error": f"PDF下载失败: {str(e)}",
            }

    async def extract_abstract_intro(self, pdf_path: str) -> dict:
        """Light extraction of abstract and introduction from PDF."""
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "abstract": "",
                "introduction": "",
                "error": "PDF文件不存在",
            }

        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            max_pages = min(len(doc), 10)
            for i in range(max_pages):
                full_text += doc[i].get_text()
            doc.close()

            abstract, introduction = self._find_sections(full_text)
            return {
                "success": True,
                "abstract": abstract,
                "introduction": introduction,
                "error": None,
            }
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return {
                "success": False,
                "abstract": "",
                "introduction": "",
                "error": f"PDF文本提取失败: {str(e)}",
            }

    def _find_sections(self, text: str) -> tuple[str, str]:
        """Heuristic section extraction."""
        text_lower = text.lower()
        abstract = ""
        introduction = ""

        abs_start = text_lower.find("abstract")
        intro_start = text_lower.find("introduction")
        intro_idx = text_lower.find("1. introduction")
        if intro_idx == -1:
            intro_idx = text_lower.find("1 introduction")

        if abs_start != -1:
            end = intro_start if intro_start > abs_start else abs_start + 2000
            abstract = text[abs_start:end].strip()[:3000]

        if intro_start != -1:
            introduction = text[intro_start:intro_start + 5000].strip()
        elif intro_idx != -1:
            introduction = text[intro_idx:intro_idx + 5000].strip()

        return abstract, introduction

    async def parse_full_text(self, arxiv_id: str, pdf_path: str) -> dict:
        """Full PDF parsing with structured section extraction."""
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "parsed_path": "",
                "sections": [],
                "error": "PDF文件不存在",
            }

        try:
            doc = fitz.open(pdf_path)

            # Extract all text page by page
            pages_text = []
            full_text = ""
            for i in range(len(doc)):
                page_text = doc[i].get_text()
                pages_text.append(page_text)
                full_text += page_text + "\n"
            doc.close()

            # Extract structured sections
            title = self._extract_title(pages_text[0] if pages_text else "")
            sections = self._extract_sections(full_text)
            references = self._extract_references(full_text)

            # Generate parsed.md
            parsed_md_path = self._write_parsed_md(arxiv_id, title, sections, references)

            logger.info(f"Full text parsed for {arxiv_id}: {len(sections)} sections")
            return {
                "success": True,
                "parsed_path": parsed_md_path,
                "title": title,
                "sections": sections,
                "references": references,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Full text parsing failed for {arxiv_id}: {e}")
            return {
                "success": False,
                "parsed_path": "",
                "sections": [],
                "error": f"全文解析失败: {str(e)}",
            }

    def _extract_title(self, first_page_text: str) -> str:
        """Extract paper title from first page."""
        lines = first_page_text.strip().split("\n")
        # Title is usually the first non-empty, non-metadata line
        for line in lines[:20]:
            line = line.strip()
            if not line:
                continue
            # Skip arXiv ID lines, copyright, etc.
            if any(skip in line.lower() for skip in ["arxiv", "http", "copyright", "©", "license"]):
                continue
            if len(line) > 20:
                return line
        return ""

    def _extract_sections(self, full_text: str) -> list[dict]:
        """Extract sections from full text using heading patterns."""
        # Patterns for section headings
        heading_patterns = [
            r"(?<=\n)\s*(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z\s\-]{3,80})\s*\n",
            r"(?<=\n)\s*(Abstract|Introduction|Related Work|Background|Method|Approach|Framework"
            r"|Experiment|Evaluation|Result|Discussion|Conclusion|Future Work|Limitation"
            r"|Acknowledgments?|Reference|Bibliography|Appendix)\s*\n",
        ]

        section_spans = []
        for pattern in heading_patterns:
            for match in re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE):
                start = match.start()
                heading = match.group(0).strip()
                section_spans.append((start, heading))

        section_spans.sort(key=lambda x: x[0])

        # Extract section content
        sections = []
        for i, (start, heading) in enumerate(section_spans):
            if i + 1 < len(section_spans):
                end = section_spans[i + 1][0]
            else:
                end = min(start + 10000, len(full_text))

            content = full_text[start:end].strip()
            # Remove the heading line from content
            content = content[len(heading):].strip()
            content = self._clean_text(content)

            sections.append({
                "heading": heading.strip(),
                "content": content[:5000],
                "char_count": len(content),
            })

        return sections

    def _extract_references(self, full_text: str) -> str:
        """Extract references section from full text."""
        ref_patterns = [
            r"(?i)references?\s*\n(.{20,}?)(?:\n\s*(?:Appendix|Supplementary|$)|\Z)",
            r"(?i)Bibliography\s*\n(.{20,}?)(?:\n\s*(?:Appendix|$)|\Z)",
        ]

        for pattern in ref_patterns:
            match = re.search(pattern, full_text, re.DOTALL)
            if match:
                refs = match.group(1).strip()
                if len(refs) > 100:
                    return refs[:8000]

        return "参考文献解析失败（PDF格式限制）"

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove hyphenation at line breaks
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        return text.strip()

    def _write_parsed_md(self, arxiv_id: str, title: str, sections: list[dict], references: str) -> str:
        """Write parsed content to parsed.md file."""
        paper_dir = self.file_manager.ensure_paper_dir(arxiv_id)
        parsed_path = os.path.join(paper_dir, "parsed.md")

        lines = []
        if title:
            lines.append(f"# {title}\n")

        for sec in sections:
            heading = sec["heading"]
            # Determine heading level
            if re.match(r"^\d+\.?\s", heading):
                depth = heading.count(".") + 1
                prefix = "#" * min(depth, 4)
            else:
                prefix = "##"
            lines.append(f"{prefix} {heading}\n")
            lines.append(sec["content"])
            lines.append("\n")

        if references:
            lines.append("## References\n")
            lines.append(references)
            lines.append("\n")

        with open(parsed_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return parsed_path

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

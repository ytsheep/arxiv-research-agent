"""Library tool: manage local paper library with database and filesystem."""

import os
import json
from datetime import datetime
from sqlalchemy import select, update, func
from app.db.database import async_session
from app.models.paper import Paper, PaperFile, PaperSummary, PaperTag
from app.storage.file_manager import FileManager
from app.core.logging import logger


class LibraryTool:
    def __init__(self):
        self.file_manager = FileManager()

    async def add_paper(
        self,
        paper: dict,
        files: dict | None = None,
        source: str = "manual_search",
        status: str = "collected",
    ) -> dict:
        """Add paper to library. Returns success dict."""
        arxiv_id = paper.get("arxiv_id", "")
        if not arxiv_id:
            return {"success": False, "arxiv_id": "", "error": "Missing arxiv_id"}

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        files = files or {}

        try:
            async with async_session() as session:
                existing = await session.execute(
                    select(Paper).where(Paper.arxiv_id == arxiv_id)
                )
                paper_obj = existing.scalar_one_or_none()

                if paper_obj:
                    # Update existing paper
                    if paper_obj.status == "deleted":
                        paper_obj.status = status
                    paper_obj.updated_at = now
                    if files.get("pdf_path"):
                        paper_obj.has_pdf = 1
                    logger.info(f"Paper {arxiv_id} already exists, updated timestamp")
                else:
                    paper_obj = Paper(
                        arxiv_id=arxiv_id,
                        title=paper.get("title", ""),
                        abstract=paper.get("abstract", ""),
                        published_date=paper.get("published_date", ""),
                        updated_date=paper.get("updated_date", ""),
                        arxiv_url=paper.get("arxiv_url", ""),
                        pdf_url=paper.get("pdf_url", ""),
                        source=source,
                        status=status,
                        has_pdf=1 if files.get("pdf_path") else 0,
                        has_parsed_doc=0,
                        has_report=0,
                        created_at=now,
                        updated_at=now,
                    )
                    paper_obj.set_authors(paper.get("authors", []))
                    paper_obj.set_categories(paper.get("categories", []))
                    session.add(paper_obj)

                await session.commit()

                # Update or create file record
                if files:
                    file_obj = await session.execute(
                        select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                    )
                    file_obj = file_obj.scalar_one_or_none()

                    if file_obj:
                        file_obj.pdf_path = files.get("pdf_path", file_obj.pdf_path)
                        file_obj.updated_at = now
                    else:
                        file_obj = PaperFile(
                            arxiv_id=arxiv_id,
                            pdf_path=files.get("pdf_path", ""),
                            metadata_path=files.get("metadata_path", ""),
                            created_at=now,
                            updated_at=now,
                        )
                        session.add(file_obj)

                    await session.commit()

                # Save metadata.json to filesystem
                self._save_metadata(arxiv_id, paper, files)

            return {"success": True, "arxiv_id": arxiv_id, "error": None}

        except Exception as e:
            logger.error(f"Failed to add paper {arxiv_id}: {e}")
            return {"success": False, "arxiv_id": arxiv_id, "error": str(e)}

    def _save_metadata(self, arxiv_id: str, paper: dict, files: dict):
        """Save metadata.json to paper directory."""
        paper_dir = self.file_manager.ensure_paper_dir(arxiv_id)
        metadata_path = os.path.join(paper_dir, "metadata.json")

        metadata = {
            "arxiv_id": arxiv_id,
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "abstract": paper.get("abstract", ""),
            "categories": paper.get("categories", []),
            "published_date": paper.get("published_date", ""),
            "updated_date": paper.get("updated_date", ""),
            "arxiv_url": paper.get("arxiv_url", ""),
            "pdf_url": paper.get("pdf_url", ""),
            "pdf_path": files.get("pdf_path", ""),
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    async def search_papers(
        self,
        keyword: str = "",
        status: str = "",
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
    ) -> dict:
        """Search papers with optional filters."""
        try:
            async with async_session() as session:
                query = select(Paper)

                if status:
                    query = query.where(Paper.status == status)
                else:
                    query = query.where(Paper.status != "deleted")

                if keyword:
                    kw = f"%{keyword}%"
                    query = query.where(
                        Paper.title.ilike(kw) | Paper.abstract.ilike(kw)
                    )

                # Count total
                count_query = select(func.count()).select_from(query.subquery())
                total = (await session.execute(count_query)).scalar() or 0

                # Paginate
                offset = (page - 1) * page_size
                if sort_by == "title":
                    order_col = Paper.title
                elif sort_by == "published_date":
                    order_col = Paper.published_date.desc()
                else:
                    order_col = Paper.created_at.desc()

                query = query.order_by(order_col).offset(offset).limit(page_size)
                result = await session.execute(query)
                papers = result.scalars().all()

                paper_list = []
                for p in papers:
                    d = p.to_dict()
                    # Get tags
                    tags_result = await session.execute(
                        select(PaperTag.tag).where(PaperTag.arxiv_id == p.arxiv_id)
                    )
                    d["tags"] = tags_result.scalars().all()
                    paper_list.append(d)

                return {
                    "success": True,
                    "total": total,
                    "papers": paper_list,
                }

        except Exception as e:
            logger.error(f"Failed to search papers: {e}")
            return {"success": False, "total": 0, "papers": [], "error": str(e)}

    async def get_paper(self, arxiv_id: str) -> dict:
        """Get a single paper by arxiv_id."""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Paper).where(Paper.arxiv_id == arxiv_id)
                )
                paper = result.scalar_one_or_none()

                if not paper:
                    return {"success": False, "paper": None, "error": "PAPER_NOT_FOUND"}

                d = paper.to_dict()

                # Get tags
                tags_result = await session.execute(
                    select(PaperTag.tag).where(PaperTag.arxiv_id == arxiv_id)
                )
                d["tags"] = tags_result.scalars().all()

                # Get file info
                files_result = await session.execute(
                    select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                )
                file_obj = files_result.scalar_one_or_none()

                return {
                    "success": True,
                    "paper": d,
                    "files": {
                        "pdf_path": file_obj.pdf_path if file_obj else "",
                        "metadata_path": file_obj.metadata_path if file_obj else "",
                        "parsed_path": file_obj.parsed_path if file_obj else "",
                        "report_path": file_obj.report_path if file_obj else "",
                    },
                }

        except Exception as e:
            logger.error(f"Failed to get paper {arxiv_id}: {e}")
            return {"success": False, "paper": None, "error": str(e)}

    async def delete_paper(self, arxiv_id: str, delete_mode: str = "soft") -> dict:
        """Delete a paper (soft delete by default)."""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Paper).where(Paper.arxiv_id == arxiv_id)
                )
                paper = result.scalar_one_or_none()

                if not paper:
                    return {"success": False, "error": "PAPER_NOT_FOUND"}

                if delete_mode == "hard":
                    await session.delete(paper)
                    # Also delete related records
                    await session.execute(
                        select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                    )
                    files_result = await session.execute(
                        select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                    )
                    file_obj = files_result.scalar_one_or_none()
                    if file_obj:
                        await session.delete(file_obj)
                else:
                    paper.status = "deleted"
                    paper.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                await session.commit()
                logger.info(f"Paper {arxiv_id} deleted ({delete_mode})")
                return {"success": True, "error": None}

        except Exception as e:
            logger.error(f"Failed to delete paper {arxiv_id}: {e}")
            return {"success": False, "error": str(e)}

    async def update_after_parse(
        self,
        arxiv_id: str,
        parsed_path: str = "",
        report_path: str = "",
    ) -> dict:
        """Update paper status and file records after parsing."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            async with async_session() as session:
                paper = await session.execute(
                    select(Paper).where(Paper.arxiv_id == arxiv_id)
                )
                paper_obj = paper.scalar_one_or_none()
                if not paper_obj:
                    return {"success": False, "error": "PAPER_NOT_FOUND"}

                paper_obj.status = "parsed"
                paper_obj.has_parsed_doc = 1
                paper_obj.has_report = 1
                paper_obj.updated_at = now

                file_obj = await session.execute(
                    select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                )
                file_obj = file_obj.scalar_one_or_none()
                if file_obj:
                    file_obj.parsed_path = parsed_path
                    file_obj.report_path = report_path
                    file_obj.updated_at = now
                else:
                    file_obj = PaperFile(
                        arxiv_id=arxiv_id,
                        parsed_path=parsed_path,
                        report_path=report_path,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(file_obj)

                await session.commit()
                return {"success": True}

        except Exception as e:
            logger.error(f"Failed to update after parse {arxiv_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_report(self, arxiv_id: str) -> dict:
        """Get report markdown from file system."""
        paper_dir = self.file_manager.get_paper_dir(arxiv_id)
        report_path = os.path.join(paper_dir, "report.md")

        if not os.path.exists(report_path):
            return {"success": False, "report_markdown": "", "error": "报告不存在"}

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                markdown = f.read()
            return {"success": True, "report_markdown": markdown, "error": None}
        except Exception as e:
            return {"success": False, "report_markdown": "", "error": str(e)}

    async def delete_report(self, arxiv_id: str) -> dict:
        """Delete report and parsed files."""
        paper_dir = self.file_manager.get_paper_dir(arxiv_id)
        report_path = os.path.join(paper_dir, "report.md")
        parsed_path = os.path.join(paper_dir, "parsed.md")

        deleted = []
        for path in [report_path, parsed_path]:
            if os.path.exists(path):
                os.remove(path)
                deleted.append(os.path.basename(path))

        try:
            async with async_session() as session:
                file_obj = await session.execute(
                    select(PaperFile).where(PaperFile.arxiv_id == arxiv_id)
                )
                file_obj = file_obj.scalar_one_or_none()
                if file_obj:
                    file_obj.parsed_path = ""
                    file_obj.report_path = ""

                paper = await session.execute(
                    select(Paper).where(Paper.arxiv_id == arxiv_id)
                )
                paper_obj = paper.scalar_one_or_none()
                if paper_obj:
                    paper_obj.has_parsed_doc = 0
                    paper_obj.has_report = 0
                    paper_obj.status = "collected"
                    paper_obj.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                await session.commit()

            return {"success": True, "deleted": deleted}
        except Exception as e:
            logger.error(f"Failed to delete report {arxiv_id}: {e}")
            return {"success": False, "error": str(e)}

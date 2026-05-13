import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    authors = Column(Text)  # JSON string
    abstract = Column(Text)
    categories = Column(Text)  # JSON string
    published_date = Column(String)
    updated_date = Column(String)
    arxiv_url = Column(String)
    pdf_url = Column(String)
    source = Column(String, default="manual_search")
    status = Column(String, default="collected")
    has_pdf = Column(Integer, default=0)
    has_parsed_doc = Column(Integer, default=0)
    has_report = Column(Integer, default=0)
    created_at = Column(String)
    updated_at = Column(String)

    def set_authors(self, authors: list[str]):
        self.authors = json.dumps(authors, ensure_ascii=False)

    def get_authors(self) -> list[str]:
        return json.loads(self.authors) if self.authors else []

    def set_categories(self, categories: list[str]):
        self.categories = json.dumps(categories, ensure_ascii=False)

    def get_categories(self) -> list[str]:
        return json.loads(self.categories) if self.categories else []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.get_authors(),
            "abstract": self.abstract,
            "categories": self.get_categories(),
            "published_date": self.published_date,
            "updated_date": self.updated_date,
            "arxiv_url": self.arxiv_url,
            "pdf_url": self.pdf_url,
            "source": self.source,
            "status": self.status,
            "has_pdf": bool(self.has_pdf),
            "has_parsed_doc": bool(self.has_parsed_doc),
            "has_report": bool(self.has_report),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PaperFile(Base):
    __tablename__ = "paper_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, nullable=False)
    pdf_path = Column(String)
    metadata_path = Column(String)
    parsed_path = Column(String)
    report_path = Column(String)
    created_at = Column(String)
    updated_at = Column(String)


class PaperSummary(Base):
    __tablename__ = "paper_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, nullable=False)
    short_summary = Column(Text)
    core_problem = Column(Text)
    method_summary = Column(Text)
    result_summary = Column(Text)
    limitation_summary = Column(Text)
    summary_source = Column(String)
    model_name = Column(String)
    created_at = Column(String)


class PaperTag(Base):
    __tablename__ = "paper_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, nullable=False)
    tag = Column(String, nullable=False)

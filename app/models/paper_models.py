from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    tldr: str = Field(description="One-sentence summary of the paper.")
    problem: str = Field(description="Core research problem the paper solves.")
    method: str = Field(description="Main method or technical approach.")
    results: str = Field(description="Key results or takeaways.")


class Paper(BaseModel):
    id: str
    title: str
    summary: str
    entry_url: str
    pdf_url: str
    published: Optional[str] = None
    updated: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    tldr: Optional[str] = None
    problem: Optional[str] = None
    method: Optional[str] = None
    results: Optional[str] = None


class DeliveryResult(BaseModel):
    channel: str
    target: str
    status: str
    error_message: Optional[str] = None


class DigestResult(BaseModel):
    generated_at: datetime
    query: str
    focus: str
    papers: List[Paper] = Field(default_factory=list)
    markdown: str = ""
    plain_text: str = ""
    tool_trace: List[str] = Field(default_factory=list)
    agent_summary: str = ""
    notified_channels: List[str] = Field(default_factory=list)
    delivery_results: List[DeliveryResult] = Field(default_factory=list)
    subscription_id: Optional[int] = None
    subscription_name: Optional[str] = None

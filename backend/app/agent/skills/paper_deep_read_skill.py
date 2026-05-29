"""Paper Deep Read Skill: resolve paper -> collect if needed -> parse -> deep report."""

import os
import json

from app.tools.library_tool import LibraryTool
from app.tools.pdf_tool import PdfTool
from app.tools.report_tool import ReportTool
from app.tools.trace_tool import TraceTool
from app.services.memory_service import ShortTermMemoryService
from app.storage.file_manager import FileManager
from app.core.logging import logger

PAPER_DEEP_READ_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "paper_deep_read_skill",
        "description": "Deep-read a paper: resolve reference, collect PDF if needed, parse full text, and generate a Chinese deep reading report. Use this when the user wants to deeply analyze or parse a specific paper.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "The original user message for intent context",
                },
                "arxiv_id": {
                    "type": "string",
                    "description": "The arXiv paper ID to deep-read, e.g. '2604.09537v1'",
                },
                "paper_ref": {
                    "type": "string",
                    "description": "Positional reference like 'the second paper' or 'the first one'. Used when arxiv_id is not provided.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID for resolving paper references from conversation history",
                },
            },
            "required": ["user_message"],
        },
    },
}


async def paper_deep_read_skill(
    user_message: str = "",
    arxiv_id: str = "",
    paper_ref: str = "",
    session_id: str = "",
) -> dict:
    trace_tool = TraceTool()
    library_tool = LibraryTool()
    pdf_tool = PdfTool()
    report_tool = ReportTool()

    trace = trace_tool.create(task_type="paper_deep_read", user_input=user_message)
    logger.info(f"[Skill:paper_deep_read trace={trace.trace_id}] arxiv_id={arxiv_id} ref={paper_ref}")

    # Step 1: Resolve paper reference
    if not arxiv_id and paper_ref:
        if session_id:
            short_memory = ShortTermMemoryService()
            last_papers = await short_memory.get_last_papers(session_id)
            resolved = _resolve_paper_ref(paper_ref, last_papers)
            if resolved:
                arxiv_id = resolved.get("arxiv_id", "")
            else:
                arxiv_id = paper_ref  # Try as raw arxiv_id

    if not arxiv_id:
        await trace_tool.complete(trace.trace_id, status="failed",
                                   error_message="Cannot resolve paper reference", trace=trace)
        return {
            "success": False,
            "trace_id": trace.trace_id,
            "message": "无法确定要精读的论文，请提供 arXiv ID 或指定具体论文。",
        }

    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="resolve_paper_ref",
        input_summary=f"arxiv_id={arxiv_id}, paper_ref={paper_ref}",
        output_summary=f"resolved arxiv_id={arxiv_id}",
    )

    # Step 2: Check library and collect if needed
    lib_result = await library_tool.get_paper(arxiv_id)
    pdf_path = ""
    if lib_result.get("success") and lib_result.get("files"):
        pdf_path = lib_result["files"].get("pdf_path", "")
        paper = lib_result.get("paper", {})
    else:
        paper = {"arxiv_id": arxiv_id, "title": "", "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}"}

    if not pdf_path:
        pdf_result = await pdf_tool.download_pdf(
            arxiv_id=arxiv_id,
            pdf_url=paper.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}"),
        )
        if not pdf_result.get("success"):
            await trace_tool.complete(trace.trace_id, status="failed",
                                       error_message=pdf_result.get("error", "PDF_DOWNLOAD_FAILED"), trace=trace)
            return {
                "success": False,
                "trace_id": trace.trace_id,
                "arxiv_id": arxiv_id,
                "message": f"PDF 下载失败: {pdf_result.get('error', '未知错误')}",
            }
        pdf_path = pdf_result["pdf_path"]
        await library_tool.add_paper(paper=paper, files={"pdf_path": pdf_path}, source="deep_read")
        await trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="paper_collect",
            input_summary=f"arxiv_id={arxiv_id}",
            output_summary=f"pdf_path={pdf_path}",
        )
    else:
        await trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="paper_collect",
            input_summary=f"arxiv_id={arxiv_id} already collected",
            output_summary=f"pdf_path={pdf_path}",
        )

    # Step 3: Parse full text
    parse_result = await pdf_tool.parse_full_text(arxiv_id=arxiv_id, pdf_path=pdf_path)
    if not parse_result.get("success"):
        await trace_tool.complete(trace.trace_id, status="failed",
                                   error_message=parse_result.get("error", "PDF_PARSE_FAILED"), trace=trace)
        return {
            "success": False,
            "trace_id": trace.trace_id,
            "arxiv_id": arxiv_id,
            "message": f"PDF 全文解析失败: {parse_result.get('error', '未知错误')}",
        }
    parsed_path = parse_result.get("parsed_path", "")
    await library_tool.update_after_parse(arxiv_id=arxiv_id, parsed_path=parsed_path)
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="pdf_parse_full_text",
        input_summary=f"arxiv_id={arxiv_id}, pdf_path={pdf_path}",
        output_summary=f"parsed_path={parsed_path}, sections={len(parse_result.get('sections', []))}",
    )

    # Step 4: Generate deep report
    file_manager = FileManager()
    paper_dir = file_manager.get_paper_dir(arxiv_id)

    # Read parsed.md content
    parsed_md_path = parsed_path or os.path.join(paper_dir, "parsed.md")
    parsed_markdown_content = ""
    if os.path.exists(parsed_md_path):
        with open(parsed_md_path, "r", encoding="utf-8") as f:
            parsed_markdown_content = f.read()

    # Load metadata
    metadata_path = os.path.join(paper_dir, "metadata.json")
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    report_result = await report_tool.generate_deep_report(
        arxiv_id=arxiv_id,
        parsed_markdown=parsed_markdown_content,
        metadata=metadata,
        sections=parse_result.get("sections"),
    )
    if not report_result.get("success"):
        await trace_tool.complete(trace.trace_id, status="failed",
                                   error_message=report_result.get("error", "REPORT_GENERATION_FAILED"), trace=trace)
        return {
            "success": False,
            "trace_id": trace.trace_id,
            "arxiv_id": arxiv_id,
            "message": f"精读报告生成失败: {report_result.get('error', '未知错误')}",
        }
    report_path = report_result.get("report_path", "")
    await library_tool.update_after_parse(arxiv_id=arxiv_id, report_path=report_path)
    await trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="generate_deep_report",
        input_summary=f"arxiv_id={arxiv_id}, parsed_path={parsed_path}",
        output_summary=f"report_path={report_path}",
    )

    # Step 5: Load report content
    report_data = await library_tool.get_report(arxiv_id)
    report_markdown = report_data.get("report_markdown", "")

    summary = report_markdown[:500] if report_markdown else "报告已生成"

    await trace_tool.complete(trace.trace_id, status="success", trace=trace)

    return {
        "success": True,
        "trace_id": trace.trace_id,
        "arxiv_id": arxiv_id,
        "message": f"论文 {arxiv_id} 精读报告已生成",
        "report_summary": summary,
        "report_markdown": report_markdown,
    }


def _resolve_paper_ref(paper_ref: str, last_papers: list[dict]) -> dict | None:
    """Resolve a positional paper reference like 'the second paper'."""
    if not last_papers:
        return None

    import re
    text = paper_ref.lower()
    digit_match = re.search(r"(\d+)", text)
    if digit_match:
        index = max(0, int(digit_match.group(1)) - 1)
        if index < len(last_papers):
            return last_papers[index]

    number_words = {
        "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
    }
    for word, index in number_words.items():
        if word in text and index < len(last_papers):
            return last_papers[index]

    return None

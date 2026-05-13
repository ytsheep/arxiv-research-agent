"""Paper service: manages paper collection, parsing, and library operations."""

import os
from app.schemas.paper import OperationResponse
from app.tools.arxiv_tool import ArxivTool
from app.tools.pdf_tool import PdfTool
from app.tools.report_tool import ReportTool
from app.tools.library_tool import LibraryTool
from app.agent.shared import orchestrator
from app.core.logging import logger


async def collect_paper(arxiv_id: str, paper_metadata: dict | None = None) -> OperationResponse:
    """Collect a paper: download PDF, save metadata, write to library."""
    trace = orchestrator.trace_tool.create(
        task_type="paper_collect",
        user_input=f"collect: {arxiv_id}",
        tags=["paper_collect", arxiv_id],
    )

    if not paper_metadata or not paper_metadata.get("title"):
        arxiv_tool = ArxivTool()
        meta_result = await arxiv_tool.get_paper_metadata(arxiv_id)
        await orchestrator.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="get_metadata",
            input_summary=f"arxiv_id={arxiv_id}",
            output_summary=f"found={'yes' if meta_result.get('success') else 'no'}",
            status="success" if meta_result.get("success") else "failed",
            error_message=meta_result.get("error", ""),
        )
        if not meta_result.get("success"):
            await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=meta_result.get("error", ""), trace=trace)
            return OperationResponse(
                success=False,
                trace_id=trace.trace_id,
                status="failed",
                message=f"获取论文元数据失败: {meta_result.get('error')}",
                error_code="ARXIV_METADATA_FAILED",
                detail=meta_result.get("error", ""),
            )
        paper_metadata = meta_result["paper"]

    pdf_url = paper_metadata.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}")

    pdf_tool = PdfTool()
    download_result = await pdf_tool.download_pdf(arxiv_id, pdf_url)
    await orchestrator.trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="pdf_download",
        input_summary=f"pdf_url={pdf_url}",
        output_summary=f"downloaded={'yes' if download_result.get('success') else 'no'}",
        status="success" if download_result.get("success") else "failed",
        error_message=download_result.get("error", ""),
    )

    if not download_result.get("success"):
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=download_result.get("error", ""), trace=trace)
        return OperationResponse(
            success=False,
            trace_id=trace.trace_id,
            status="failed",
            message=f"PDF下载失败: {download_result.get('error')}",
            error_code="PDF_DOWNLOAD_FAILED",
            detail=download_result.get("error", ""),
        )

    library_tool = LibraryTool()
    library_result = await library_tool.add_paper(
        paper=paper_metadata,
        files={"pdf_path": download_result.get("pdf_path", ""), "metadata_path": ""},
        source="manual_search",
        status="collected",
    )
    await orchestrator.trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="library_write",
        input_summary=f"arxiv_id={arxiv_id}",
        output_summary=f"saved={'yes' if library_result.get('success') else 'no'}",
        status="success" if library_result.get("success") else "failed",
        error_message=library_result.get("error", ""),
    )

    if not library_result.get("success"):
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=library_result.get("error", ""), trace=trace)
        return OperationResponse(
            success=False,
            trace_id=trace.trace_id,
            status="failed",
            message=f"论文入库失败: {library_result.get('error')}",
            error_code="LIBRARY_WRITE_FAILED",
            detail=library_result.get("error", ""),
        )

    await orchestrator.trace_tool.complete(trace.trace_id, status="success", trace=trace)
    logger.info(f"Paper {arxiv_id} collected successfully, trace={trace.trace_id}")

    return OperationResponse(
        success=True,
        trace_id=trace.trace_id,
        status="success",
        message=f"论文 {arxiv_id} 收藏成功",
    )


async def parse_paper(arxiv_id: str) -> OperationResponse:
    """Parse a paper: full text extraction, report generation, update library."""
    trace = orchestrator.trace_tool.create(
        task_type="paper_parse",
        user_input=f"parse: {arxiv_id}",
        tags=["paper_parse", arxiv_id],
    )

    library_tool = LibraryTool()
    paper_result = await library_tool.get_paper(arxiv_id)

    if not paper_result.get("success"):
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message="PAPER_NOT_FOUND", trace=trace)
        return OperationResponse(
            success=False,
            trace_id=trace.trace_id,
            status="failed",
            message=f"论文 {arxiv_id} 不在本地库中，请先收藏",
            error_code="PAPER_NOT_FOUND",
        )

    paper = paper_result.get("paper", {})
    files = paper_result.get("files", {})
    pdf_path = files.get("pdf_path", "")

    if not pdf_path or not os.path.exists(pdf_path):
        pdf_tool = PdfTool()
        pdf_url = paper.get("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}")
        download_result = await pdf_tool.download_pdf(arxiv_id, pdf_url)
        await orchestrator.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="pdf_download",
            status="success" if download_result.get("success") else "failed",
            output_summary=f"path={download_result.get('pdf_path', 'none')}",
            error_message=download_result.get("error", ""),
        )
        if not download_result.get("success"):
            await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=download_result.get("error", ""), trace=trace)
            return OperationResponse(
                success=False,
                trace_id=trace.trace_id,
                status="failed",
                message=f"PDF下载失败: {download_result.get('error')}",
                error_code="PDF_DOWNLOAD_FAILED",
            )
        pdf_path = download_result["pdf_path"]

    pdf_tool = PdfTool()
    parse_result = await pdf_tool.parse_full_text(arxiv_id, pdf_path)
    await orchestrator.trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="pdf_parse_full_text",
        status="success" if parse_result.get("success") else "failed",
        output_summary=f"sections={len(parse_result.get('sections', []))}",
        error_message=parse_result.get("error", ""),
    )
    if not parse_result.get("success"):
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=parse_result.get("error", ""), trace=trace)
        return OperationResponse(
            success=False,
            trace_id=trace.trace_id,
            status="failed",
            message=f"全文解析失败: {parse_result.get('error')}",
            error_code="PDF_PARSE_FAILED",
        )

    parsed_path = parse_result.get("parsed_path", "")
    parsed_markdown = ""
    if parsed_path and os.path.exists(parsed_path):
        with open(parsed_path, "r", encoding="utf-8") as f:
            parsed_markdown = f.read()

    report_tool = ReportTool()
    report_result = await report_tool.generate_deep_report(
        arxiv_id=arxiv_id,
        parsed_markdown=parsed_markdown,
        metadata=paper,
        sections=parse_result.get("sections", []),
    )
    await orchestrator.trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="deep_report_generation",
        status="success" if report_result.get("success") else "failed",
        output_summary=f"report_path={report_result.get('report_path', 'none')}",
        error_message=report_result.get("error", ""),
    )
    if not report_result.get("success"):
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=report_result.get("error", ""), trace=trace)
        return OperationResponse(
            success=False,
            trace_id=trace.trace_id,
            status="failed",
            message=f"报告生成失败: {report_result.get('error')}",
            error_code="REPORT_GENERATION_FAILED",
        )

    update_result = await library_tool.update_after_parse(
        arxiv_id=arxiv_id,
        parsed_path=parsed_path,
        report_path=report_result.get("report_path", ""),
    )
    await orchestrator.trace_tool.log_step(
        trace_id=trace.trace_id,
        step_name="library_update",
        status="success" if update_result.get("success") else "failed",
    )

    await orchestrator.trace_tool.complete(trace.trace_id, status="success", trace=trace)
    logger.info(f"Paper {arxiv_id} parsed successfully, trace={trace.trace_id}")

    return OperationResponse(
        success=True,
        trace_id=trace.trace_id,
        status="success",
        message=f"论文 {arxiv_id} 解析完成",
    )

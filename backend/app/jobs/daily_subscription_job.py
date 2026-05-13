"""Daily subscription job: search, filter, deliver papers for a subscription."""

from datetime import datetime
from app.tools.subscription_tool import SubscriptionTool
from app.tools.arxiv_tool import ArxivTool
from app.tools.rerank_tool import RerankTool
from app.tools.notify_tool import NotifyTool
from app.tools.library_tool import LibraryTool
from app.tools.pdf_tool import PdfTool
from app.agent.shared import orchestrator
from app.core.logging import logger


async def run_daily_subscription(subscription_id: int, dry_run: bool = False) -> dict:
    """Execute a single subscription run."""
    sub_tool = SubscriptionTool()
    sub_result = await sub_tool.get(subscription_id)

    if not sub_result.get("success"):
        return {"success": False, "trace_id": "", "error": "Subscription not found"}

    sub = sub_result["subscription"]
    run_date = datetime.now().strftime("%Y-%m-%d")

    trace = orchestrator.trace_tool.create(
        task_type="subscription_run",
        user_input=f"subscription_run: {sub.get('name', '')} (id={subscription_id})",
        tags=["subscription_run", f"sub_{subscription_id}"],
    )

    try:
        # Step 1: Search arXiv for each topic
        arxiv_tool = ArxivTool()
        rerank_tool = RerankTool()
        all_papers: list[dict] = []
        topics = sub.get("topics", [])
        categories = sub.get("categories", [])
        candidate_k = sub.get("candidate_k", 20)
        top_n = sub.get("top_n", 2)

        for topic in topics:
            search_result = await arxiv_tool.search(
                query=topic,
                max_results=candidate_k,
                categories=categories if categories else None,
            )
            if search_result.get("success"):
                all_papers.extend(search_result.get("papers", []))

        # Deduplicate by arxiv_id
        seen = set()
        unique_papers = []
        for p in all_papers:
            aid = p.get("arxiv_id", "")
            if aid and aid not in seen:
                seen.add(aid)
                unique_papers.append(p)

        await orchestrator.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="arxiv_search",
            input_summary=f"topics={topics}, candidate_k={candidate_k}",
            output_summary=f"found={len(unique_papers)} unique papers",
        )

        if not unique_papers:
            await orchestrator.trace_tool.complete(trace.trace_id, status="success")
            await sub_tool.record_run(
                subscription_id=subscription_id,
                run_date=run_date,
                selected_papers=[],
                status="success",
                trace_id=trace.trace_id,
            )
            return {"success": True, "trace_id": trace.trace_id, "paper_count": 0, "error": None}

        # Step 2: Rerank across all topics
        combined_query = " ".join(topics)
        ranked = await rerank_tool.rerank(query=combined_query, papers=unique_papers, top_n=top_n)
        selected_papers = ranked.get("ranked_papers", [])
        await orchestrator.trace_tool.log_step(
            trace_id=trace.trace_id,
            step_name="candidate_rerank",
            input_summary=f"candidates={len(unique_papers)}, top_n={top_n}",
            output_summary=f"selected={len(selected_papers)}",
        )

        if dry_run:
            await orchestrator.trace_tool.complete(trace.trace_id, status="success")
            return {
                "success": True,
                "trace_id": trace.trace_id,
                "paper_count": len(selected_papers),
                "papers": selected_papers,
                "dry_run": True,
            }

        # Step 3: Auto-collect papers to library
        if not sub.get("auto_parse_full_text"):
            library_tool = LibraryTool()
            pdf_tool = PdfTool()
            collected_count = 0
            for paper in selected_papers:
                arxiv_id = paper.get("arxiv_id", "")
                pdf_url = paper.get("pdf_url", "")
                # Download PDF
                dl_result = await pdf_tool.download_pdf(arxiv_id, pdf_url)
                pdf_path = dl_result.get("pdf_path", "")
                # Add to library
                await library_tool.add_paper(
                    paper=paper,
                    files={"pdf_path": pdf_path},
                    source="subscription",
                    status="collected",
                )
                collected_count += 1

            await orchestrator.trace_tool.log_step(
                trace_id=trace.trace_id,
                step_name="auto_collect",
                input_summary=f"papers_to_collect={len(selected_papers)}",
                output_summary=f"collected={collected_count}",
            )

        # Step 4: Build daily digest
        digest = _build_daily_digest(sub["name"], selected_papers, run_date)

        # Step 5: Send notifications
        sent_email = False
        sent_feishu = False
        notify_tool = NotifyTool()

        if sub.get("email_enabled") and sub.get("email_to"):
            email_to = [e.strip() for e in sub["email_to"].split(",") if e.strip()]
            if email_to:
                email_result = await notify_tool.send_email(
                    to=email_to,
                    subject=f"[arXiv Agent] {sub['name']} - {run_date}",
                    content_markdown=digest,
                )
                sent_email = email_result.get("sent", False)
                await orchestrator.trace_tool.log_step(
                    trace_id=trace.trace_id,
                    step_name="email_send",
                    input_summary=f"to={email_to}",
                    output_summary=f"sent={sent_email}",
                    status="success" if sent_email else "failed",
                    error_message=email_result.get("error", ""),
                )

        if sub.get("feishu_enabled") and sub.get("feishu_webhook_ref"):
            feishu_result = await notify_tool.send_feishu(
                webhook_ref=sub["feishu_webhook_ref"],
                title=f"📄 {sub['name']} - 今日论文精选",
                content_markdown=digest,
            )
            sent_feishu = feishu_result.get("sent", False)
            await orchestrator.trace_tool.log_step(
                trace_id=trace.trace_id,
                step_name="feishu_send",
                output_summary=f"sent={sent_feishu}",
                status="success" if sent_feishu else "failed",
                error_message=feishu_result.get("error", ""),
            )

        # Step 6: Record run
        await sub_tool.record_run(
            subscription_id=subscription_id,
            run_date=run_date,
            selected_papers=selected_papers,
            sent_email=sent_email,
            sent_feishu=sent_feishu,
            status="success",
            trace_id=trace.trace_id,
        )

        await orchestrator.trace_tool.complete(trace.trace_id, status="success")
        logger.info(
            f"Subscription run complete: sub_id={subscription_id}, "
            f"papers={len(selected_papers)}, email={sent_email}, feishu={sent_feishu}"
        )

        return {
            "success": True,
            "trace_id": trace.trace_id,
            "paper_count": len(selected_papers),
            "sent_email": sent_email,
            "sent_feishu": sent_feishu,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Subscription run failed for id={subscription_id}: {e}")
        await orchestrator.trace_tool.complete(trace.trace_id, status="failed", error_message=str(e))
        await sub_tool.record_run(
            subscription_id=subscription_id,
            run_date=run_date,
            selected_papers=[],
            status="failed",
            error_message=str(e),
            trace_id=trace.trace_id,
        )
        return {"success": False, "trace_id": trace.trace_id, "error": str(e)}


def _build_daily_digest(sub_name: str, papers: list[dict], run_date: str) -> str:
    """Build daily digest markdown."""
    lines = []
    lines.append(f"# {sub_name}\n")
    lines.append(f"**日期**: {run_date}")
    lines.append(f"**论文数量**: {len(papers)}\n")
    lines.append("---\n")

    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "无标题")
        arxiv_id = paper.get("arxiv_id", "")
        authors = paper.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += " 等"
        else:
            authors_str = str(authors)

        lines.append(f"### {i}. {title}\n")
        lines.append(f"- **arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})")
        lines.append(f"- **作者**: {authors_str}")

        summary = paper.get("summary", paper.get("abstract", ""))
        if summary:
            lines.append(f"- **摘要**: {summary[:300]}")
        lines.append("")

    lines.append("---\n")
    lines.append("*本邮件由 arXiv Paper Agent 自动生成*")
    return "\n".join(lines)

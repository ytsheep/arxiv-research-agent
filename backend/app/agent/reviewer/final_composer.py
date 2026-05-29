"""Final Composer: builds the final user-facing response from all task outputs."""

from app.tools.llm_client import llm_client
from app.core.logging import logger


class FinalComposer:
    """Synthesizes a user-facing final message from multi-agent task outputs."""

    async def compose(self, task_outputs: dict[str, dict], user_message: str, trace_id: str, state_summary: dict) -> dict:
        """Build final_response dict.

        Args:
            task_outputs: dict[task_id, output_dict] from executed tasks
            user_message: original user request
            trace_id: workflow trace ID
            state_summary: high-level state summary (task plan status, etc.)
        """
        papers = self._extract_papers(task_outputs)
        comparison = self._extract_comparison(task_outputs)
        selected = self._extract_selected_paper(task_outputs)
        report = self._extract_report(task_outputs)
        survey = self._extract_survey(task_outputs)

        if llm_client.available:
            message = await self._llm_summary(user_message, papers, comparison, selected, report, survey, state_summary)
        else:
            message = self._template_summary(papers, comparison, selected, report, state_summary)

        return {
            "success": True,
            "type": "workflow_result",
            "trace_id": trace_id,
            "message": message,
            "papers": papers,
            "metadata": {
                "comparison": comparison,
                "selected_paper": selected,
                "report_markdown": report,
                "survey_markdown": survey,
                "task_summary": state_summary.get("task_summary", []),
            },
        }

    def _extract_papers(self, task_outputs: dict) -> list[dict]:
        for output in task_outputs.values():
            papers = output.get("papers", [])
            if papers:
                return papers
        return []

    def _extract_comparison(self, task_outputs: dict) -> dict | None:
        for output in task_outputs.values():
            comp = output.get("comparison")
            if comp:
                return comp
        return None

    def _extract_selected_paper(self, task_outputs: dict) -> dict | None:
        for output in task_outputs.values():
            sp = output.get("selected_paper")
            if sp:
                return sp
        return None

    def _extract_report(self, task_outputs: dict) -> str:
        for output in task_outputs.values():
            rm = output.get("report_markdown")
            if rm:
                return rm[:10000]  # Truncate for state
        return ""

    def _extract_survey(self, task_outputs: dict) -> str:
        for output in task_outputs.values():
            sm = output.get("survey_markdown")
            if sm:
                return sm
        return ""

    async def _llm_summary(self, user_message, papers, comparison, selected, report, survey, state_summary) -> str:
        parts = [f"User request: {user_message}"]
        parts.append(f"Found {len(papers)} papers.")

        paper_list = "\n".join(
            f"- {p.get('title', p.get('arxiv_id', ''))}" for p in papers[:5]
        )
        parts.append(f"Papers:\n{paper_list}")

        if selected:
            parts.append(f"Selected best paper: {selected.get('title', selected.get('arxiv_id', ''))}")

        tasks = state_summary.get("task_summary", [])
        task_text = "\n".join(
            f"- {tsk.get('task_type', tsk.get('task_id', ''))}: {tsk.get('status', '')}"
            for tsk in tasks
        )
        parts.append(f"Tasks executed:\n{task_text}")

        prompt = (
            "Write a concise Chinese summary of the completed research workflow.\n\n"
            + "\n".join(parts)
            + "\n\nKeep it under 5 sentences. Mention what was found, compared, selected, and any key insights."
        )

        try:
            result = await llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=512,
            )
            if result.get("success") and result.get("content"):
                return result["content"]
        except Exception:
            pass

        return self._template_summary(papers, comparison, selected, report, state_summary)

    def _template_summary(self, papers, comparison, selected, report, state_summary) -> str:
        lines = []
        tasks = state_summary.get("task_summary", [])
        completed_count = sum(1 for t in tasks if t.get("status") == "completed")
        failed_count = sum(1 for t in tasks if t.get("status") == "failed")

        lines.append(f"任务执行完成: {completed_count}/{len(tasks)} 个子任务成功")
        if failed_count > 0:
            lines.append(f"{failed_count} 个任务失败")

        if papers:
            lines.append(f"\n检索到 {len(papers)} 篇论文:")
            for p in papers[:5]:
                lines.append(f"- {p.get('title', p.get('arxiv_id', ''))}")

        if comparison:
            lines.append(f"\n对比分析: {comparison.get('overview', '已完成多维度对比')}")

        if selected:
            sel_title = selected.get("title", selected.get("arxiv_id", ""))
            lines.append(f"\n推荐论文: {sel_title}")

        if report:
            lines.append("\n精读报告已生成")

        return "\n".join(lines) if lines else "任务执行完成。"

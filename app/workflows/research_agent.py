from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from app.clients import ArxivClient
from app.config import Settings
from app.models import DigestResult, Paper, PaperSummary


DEFAULT_TOP_K = 5
DEFAULT_MAX_RESULTS = 50


class ResearchState(MessagesState):
    focus: str
    top_k: int
    max_results: int


@dataclass
class AgentRunContext:
    papers_by_id: dict[str, Paper] = field(default_factory=dict)
    selected_papers: list[Paper] = field(default_factory=list)
    tool_trace: list[str] = field(default_factory=list)


class ArxivResearchWorkflow:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.arxiv_client = ArxivClient(settings)

    def run(
        self,
        query: str,
        focus: str,
        api_key: str,
        max_results: int | None = None,
        top_k: int | None = None,
    ) -> DigestResult:
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY is required.")

        resolved_max_results = max_results or DEFAULT_MAX_RESULTS
        resolved_top_k = top_k or DEFAULT_TOP_K
        context = AgentRunContext()

        tools = self._build_tools(context=context, api_key=api_key, top_k=resolved_top_k)
        llm = self._build_llm(api_key=api_key).bind_tools(tools)
        graph = self._build_graph(llm=llm, tools=tools)

        final_state = graph.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "focus": focus,
                "top_k": resolved_top_k,
                "max_results": resolved_max_results,
            }
        )
        final_message = final_state["messages"][-1].content if final_state.get("messages") else ""
        return self.render_digest_result(
            query=query,
            focus=focus,
            papers=context.selected_papers,
            tool_trace=context.tool_trace,
            agent_summary=str(final_message),
        )

    def render_digest_result(
        self,
        *,
        query: str,
        focus: str,
        papers: list[Paper],
        tool_trace: list[str],
        agent_summary: str,
        generated_at: datetime | None = None,
        subscription_id: int | None = None,
        subscription_name: str | None = None,
    ) -> DigestResult:
        generated_at = generated_at or datetime.now()
        if papers:
            markdown = self._build_markdown(focus=focus, papers=papers, agent_summary=agent_summary)
            plain_text = self._build_plain_text(focus=focus, papers=papers)
        else:
            markdown = self._build_empty_markdown(focus=focus)
            plain_text = self._build_empty_text(focus=focus)

        return DigestResult(
            generated_at=generated_at,
            query=query,
            focus=focus,
            papers=papers,
            markdown=markdown,
            plain_text=plain_text,
            tool_trace=tool_trace,
            agent_summary=agent_summary,
            subscription_id=subscription_id,
            subscription_name=subscription_name,
        )

    def _build_tools(
        self,
        *,
        context: AgentRunContext,
        api_key: str,
        top_k: int,
    ) -> list[Any]:
        @tool
        def search_arxiv(query: str, max_results: int) -> list[dict[str, Any]]:
            """Search the latest arXiv papers for a query and return compact paper metadata."""

            papers = self.arxiv_client.search(search_query=query, max_results=max_results)
            context.papers_by_id = {paper.id: paper for paper in papers}
            context.tool_trace.append(
                f"search_arxiv(query={query!r}, max_results={max_results}) -> {len(papers)} papers"
            )
            return [
                {
                    "id": paper.id,
                    "title": paper.title,
                    "published": paper.published,
                    "authors": paper.authors,
                    "summary": paper.summary,
                    "entry_url": paper.entry_url,
                }
                for paper in papers
            ]

        @tool
        def summarize_papers(paper_ids: list[str], focus: str) -> list[dict[str, Any]]:
            """Summarize up to the top-k selected papers for the current research focus."""

            unique_ids: list[str] = []
            for paper_id in paper_ids:
                if paper_id in context.papers_by_id and paper_id not in unique_ids:
                    unique_ids.append(paper_id)

            selected = [context.papers_by_id[paper_id] for paper_id in unique_ids[:top_k]]
            if not selected:
                context.selected_papers = []
                context.tool_trace.append("summarize_papers(paper_ids=[]) -> 0 papers")
                return []

            structured_llm = self._build_llm(api_key=api_key).with_structured_output(PaperSummary)
            summarized: list[Paper] = []
            for paper in selected:
                prompt = (
                    "你正在帮助整理 arXiv 论文订阅日报，请阅读下面的论文信息并用中文输出。\n"
                    f"研究关键词：{focus}\n"
                    f"论文标题：{paper.title}\n"
                    f"论文摘要：{paper.summary}\n"
                    "请返回：\n"
                    "1. tldr：一句话总结\n"
                    "2. problem：核心问题\n"
                    "3. method：主要方法\n"
                    "4. results：关键结果"
                )
                result: PaperSummary = structured_llm.invoke(prompt)
                summarized.append(
                    paper.model_copy(
                        update={
                            "tldr": result.tldr,
                            "problem": result.problem,
                            "method": result.method,
                            "results": result.results,
                        }
                    )
                )

            context.selected_papers = summarized
            context.tool_trace.append(
                f"summarize_papers(paper_ids={unique_ids[:top_k]!r}, focus={focus!r}) -> "
                f"{len(summarized)} papers"
            )
            return [paper.model_dump() for paper in summarized]

        return [search_arxiv, summarize_papers]

    def _build_graph(self, *, llm: ChatOpenAI, tools: list[Any]):
        def call_agent(state: ResearchState):
            system_prompt = self._build_system_prompt(
                focus=state["focus"],
                max_results=state["max_results"],
                top_k=state["top_k"],
            )
            response = llm.invoke([SystemMessage(content=system_prompt), *state["messages"]])
            return {"messages": [response]}

        def route_after_agent(state: ResearchState):
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"
            return "end"

        workflow = StateGraph(ResearchState)
        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", ToolNode(tools))
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "end": END})
        workflow.add_edge("tools", "agent")
        return workflow.compile()

    def _build_llm(self, *, api_key: str) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.settings.llm_model,
            api_key=api_key,
            base_url=self.settings.dashscope_base_url,
            max_tokens=2048,
            temperature=0.1,
        )

    @staticmethod
    def _build_system_prompt(*, focus: str, max_results: int, top_k: int) -> str:
        return (
            "You are an arXiv research agent with tool-calling abilities.\n"
            "You must use tools before answering.\n"
            f"Research focus: {focus}\n"
            f"Search budget: fetch up to {max_results} papers, then keep at most {top_k} papers.\n"
            "Workflow requirements:\n"
            "1. Call search_arxiv first.\n"
            "2. Pick the most relevant latest papers.\n"
            "3. Call summarize_papers once with the selected paper ids.\n"
            "4. After tool calls are complete, provide a short Chinese summary explaining why the final "
            "papers are relevant to the focus."
        )

    @staticmethod
    def _build_markdown(*, focus: str, papers: List[Paper], agent_summary: str) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"## {today} arXiv 每日精选论文",
            "",
            f"> 关键词：{focus}",
            "",
        ]

        if agent_summary.strip():
            lines.extend(["### Agent 总结", agent_summary.strip(), ""])

        lines.extend([f"### 精选论文（{len(papers)} 篇）", ""])

        for index, paper in enumerate(papers, start=1):
            lines.extend(
                [
                    f"#### {index}. {paper.title}",
                    f"- 作者：{', '.join(paper.authors) if paper.authors else '未知'}",
                    f"- 发布时间：{paper.published or '未知'}",
                    f"- arXiv：[{paper.entry_url}]({paper.entry_url})",
                    f"- PDF：[{paper.pdf_url}]({paper.pdf_url})",
                    f"- 一句话总结：{paper.tldr or paper.summary}",
                    f"- 核心问题：{paper.problem or '暂无'}",
                    f"- 方法：{paper.method or '暂无'}",
                    f"- 结果：{paper.results or '暂无'}",
                    "",
                ]
            )

        return "\n".join(lines).strip()

    @staticmethod
    def _build_plain_text(*, focus: str, papers: List[Paper]) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"{today} arXiv 每日精选论文",
            f"关键词：{focus}",
            "",
        ]
        for index, paper in enumerate(papers, start=1):
            lines.extend(
                [
                    f"{index}. {paper.title}",
                    f"arXiv：{paper.entry_url}",
                    f"PDF：{paper.pdf_url}",
                    f"一句话总结：{paper.tldr or paper.summary}",
                    f"核心问题：{paper.problem or '暂无'}",
                    f"方法：{paper.method or '暂无'}",
                    f"结果：{paper.results or '暂无'}",
                    "",
                ]
            )
        return "\n".join(lines).strip()

    @staticmethod
    def _build_empty_markdown(*, focus: str) -> str:
        return (
            "## arXiv 每日精选论文\n\n"
            f"> 关键词：{focus}\n\n"
            "今天没有筛选到新的高相关论文。"
        )

    @staticmethod
    def _build_empty_text(*, focus: str) -> str:
        return (
            "arXiv 每日精选论文\n"
            f"关键词：{focus}\n"
            "今天没有筛选到新的高相关论文。"
        )

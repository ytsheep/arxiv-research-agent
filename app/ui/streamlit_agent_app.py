from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.api.contracts import (
    RecipientPayload,
    SubscriptionCreateRequest,
    SubscriptionUpdateRequest,
)
from app.config import get_settings
from app.db import init_db
from app.services import DailyDigestService, SubscriptionService


DEFAULT_QUERY = "cat:cs.AI OR cat:cs.CL"
DEFAULT_FOCUS = "LLM Agent, RAG, reasoning, tool use, multi-agent systems"
DEFAULT_TIMEZONE = "Asia/Shanghai"


def _build_runtime_service(api_key: str) -> DailyDigestService:
    settings = get_settings().model_copy(update={"dashscope_api_key": api_key})
    return DailyDigestService(settings)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --bg: #f4efe6;
            --panel: rgba(255, 251, 245, 0.86);
            --panel-strong: rgba(255, 248, 239, 0.96);
            --ink: #13211d;
            --muted: #5d6a66;
            --line: rgba(19, 33, 29, 0.12);
            --accent: #0f766e;
            --accent-soft: rgba(15, 118, 110, 0.12);
            --warm: #d97706;
            --warm-soft: rgba(217, 119, 6, 0.10);
            --danger: #b42318;
            --shadow: 0 20px 60px rgba(19, 33, 29, 0.10);
        }

        html, body, [class*="css"] {
            font-family: "IBM Plex Sans", sans-serif;
            color: var(--ink);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.16), transparent 32%),
                radial-gradient(circle at top right, rgba(217, 119, 6, 0.14), transparent 28%),
                linear-gradient(180deg, #f7f2ea 0%, #f1ebe1 100%);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
            letter-spacing: -0.02em;
            color: var(--ink);
        }

        .hero-shell {
            padding: 1.6rem 1.7rem;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255,255,255,0.78), rgba(255,248,239,0.92)),
                linear-gradient(120deg, rgba(15,118,110,0.12), rgba(217,119,6,0.10));
            border: 1px solid rgba(255,255,255,0.65);
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        .hero-shell:before {
            content: "";
            position: absolute;
            inset: auto -12% -55% auto;
            width: 280px;
            height: 280px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(15,118,110,0.18), transparent 70%);
        }

        .eyebrow {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(19, 33, 29, 0.06);
            color: var(--muted);
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: clamp(2rem, 5vw, 3.4rem);
            line-height: 0.98;
            margin: 0;
        }

        .hero-copy {
            color: var(--muted);
            max-width: 760px;
            font-size: 1rem;
            line-height: 1.7;
            margin-top: 0.9rem;
        }

        .metric-card {
            background: var(--panel);
            border: 1px solid rgba(255,255,255,0.7);
            backdrop-filter: blur(16px);
            border-radius: 22px;
            padding: 1rem 1rem 1.1rem;
            box-shadow: 0 14px 40px rgba(19, 33, 29, 0.08);
            min-height: 124px;
        }

        .metric-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            margin-bottom: 0.55rem;
        }

        .metric-value {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.95rem;
            line-height: 1;
            margin-bottom: 0.4rem;
            color: var(--ink);
        }

        .metric-meta {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .section-card {
            background: var(--panel-strong);
            border: 1px solid rgba(255,255,255,0.72);
            border-radius: 26px;
            padding: 1.25rem 1.25rem 1.35rem;
            box-shadow: 0 14px 46px rgba(19, 33, 29, 0.08);
        }

        .section-kicker {
            display: inline-block;
            padding: 0.26rem 0.62rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 0.77rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.85rem;
        }

        .section-title {
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.35rem;
            margin: 0 0 0.45rem 0;
        }

        .section-copy {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.65;
            margin-bottom: 1rem;
        }

        .micro-card {
            background: rgba(255,255,255,0.62);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            margin-bottom: 0.8rem;
        }

        .micro-label {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.3rem;
        }

        .micro-title {
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 0.3rem;
        }

        .micro-meta {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 999px;
            margin-right: 0.35rem;
            background: var(--accent);
        }

        .status-warn { background: var(--warm); }
        .status-danger { background: var(--danger); }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.6rem;
            background: rgba(255,255,255,0.4);
            border-radius: 18px;
            padding: 0.4rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            border-radius: 14px;
            padding: 0 1rem;
            color: var(--muted);
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(255, 248, 239, 0.92) !important;
            color: var(--ink) !important;
            box-shadow: inset 0 0 0 1px rgba(15,118,110,0.18);
        }

        [data-testid="stSidebar"] {
            background: rgba(247, 242, 234, 0.92);
            border-right: 1px solid rgba(19, 33, 29, 0.08);
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 46px;
            border-radius: 14px;
            border: 1px solid rgba(15,118,110,0.24);
            background: linear-gradient(180deg, #127f75 0%, #0f6f68 100%);
            color: white;
            font-weight: 700;
            box-shadow: 0 12px 30px rgba(15, 118, 110, 0.18);
        }

        .stButton > button:hover {
            border-color: rgba(15,118,110,0.38);
            background: linear-gradient(180deg, #15897f 0%, #11746c 100%);
        }

        .stButton > button:focus {
            outline: 3px solid rgba(15,118,110,0.22);
            outline-offset: 1px;
        }

        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            border-radius: 14px !important;
            background: rgba(255,255,255,0.75) !important;
        }

        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            background: rgba(255,255,255,0.75) !important;
        }

        .stDataFrame, .stTable {
            border-radius: 18px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _parse_multiline(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        normalized = line.strip()
        if normalized and normalized not in items:
            items.append(normalized)
    return items


def _build_recipient_payloads(email_text: str, feishu_text: str) -> list[RecipientPayload]:
    recipients: list[RecipientPayload] = []
    for email in _parse_multiline(email_text):
        recipients.append(RecipientPayload(channel="email", target=email, enabled=True))
    for webhook in _parse_multiline(feishu_text):
        recipients.append(RecipientPayload(channel="feishu", target=webhook, enabled=True))
    return recipients


def _render_hero(subscription_count: int, enabled_count: int, recipient_count: int, scan_minutes: int) -> None:
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="eyebrow">Research Studio</div>
            <h1 class="hero-title">Discover fresh papers.<br/>Ship a cleaner daily signal.</h1>
            <div class="hero-copy">
                把实时检索、精选摘要、定时订阅和多接收人投递放在同一个控制台里管理。
                这版界面围绕“研究员日常工作流”设计：先探索，再沉淀成订阅，最后追踪执行结果。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    metrics = st.columns(4)
    cards = [
        ("订阅总数", str(subscription_count), "当前数据库中的全部订阅"),
        ("启用中", str(enabled_count), "会参与定时扫描与自动执行"),
        ("接收端", str(recipient_count), "邮箱与飞书 webhook 的总绑定数"),
        ("扫描频率", f"{scan_minutes} min", "调度器统一扫描 due 订阅"),
    ]
    for column, (label, value, meta) in zip(metrics, cards):
        column.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-meta">{meta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_sidebar(settings, subscriptions) -> str:
    enabled_count = len([item for item in subscriptions if item.enabled])
    runtime_api_key = st.sidebar.text_input(
        "DashScope API Key",
        value=settings.dashscope_api_key,
        type="password",
        help="用于 LangGraph Agent 调用和结构化论文总结。",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Runtime")
    st.sidebar.markdown(
        f"""
        <div class="micro-card">
            <div class="micro-label">Scheduler</div>
            <div class="micro-title"><span class="status-dot"></span>运行中</div>
            <div class="micro-meta">每 {settings.scheduler_scan_interval_minutes} 分钟扫描一次到期订阅。</div>
        </div>
        <div class="micro-card">
            <div class="micro-label">Subscriptions</div>
            <div class="micro-title">{len(subscriptions)} total / {enabled_count} enabled</div>
            <div class="micro-meta">支持 query 与 keywords 二合一配置，支持多接收人投递。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("### Design Notes")
    st.sidebar.caption(
        "采用检索工作台 + 订阅控制台双区结构，保证高频检索任务和低频配置任务各自聚焦。"
    )
    return runtime_api_key


def _render_search_tab(runtime_api_key: str) -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-kicker">Live Search</div>
            <div class="section-title">即时探索新的研究方向</div>
            <div class="section-copy">
                适合先试探关键词、评估召回质量，再决定是否沉淀为长期订阅。
                如果不写完整 arXiv query，也可以只填关键词列表。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    with st.form("search_form", clear_on_submit=False):
        col1, col2 = st.columns([1.1, 1.2], gap="large")
        with col1:
            query = st.text_input(
                "arXiv Query",
                value=DEFAULT_QUERY,
                help="如果你已经知道 arXiv 语法，直接填写完整 query。",
            )
            keywords_text = st.text_area(
                "Keywords Fallback",
                value="",
                height=140,
                help="当 query 留空时，会自动使用这些关键词构造查询语句；一行一个。",
                placeholder="multi-agent systems\nreasoning\nrag",
            )
        with col2:
            focus = st.text_area(
                "研究关键词 / Focus",
                value=DEFAULT_FOCUS,
                height=140,
                help="用于指导 Agent 选择哪些论文值得保留和总结。",
            )
            metric_cols = st.columns(2)
            top_k = metric_cols[0].number_input("输出论文数", min_value=1, max_value=20, value=5)
            max_results = metric_cols[1].number_input("初始抓取量", min_value=5, max_value=100, value=50)
        submitted = st.form_submit_button("运行 Research Agent", use_container_width=True)

    if not submitted:
        return

    if not runtime_api_key:
        st.error("请先在侧边栏填写 DashScope API Key。")
        return

    service = _build_runtime_service(runtime_api_key)
    keywords = _parse_multiline(keywords_text)
    try:
        with st.spinner("正在抓取 arXiv 论文、筛选结果并生成摘要..."):
            result = service.generate_digest(
                query=query.strip() or None,
                keywords=keywords,
                focus=focus,
                top_k=int(top_k),
                max_results=int(max_results),
                api_key=runtime_api_key,
            )
    except Exception as exc:
        st.error(f"运行失败：{exc}")
        return

    ribbon = st.columns([1.2, 1, 1], gap="medium")
    ribbon[0].success(f"完成，共保留 {len(result.papers)} 篇论文")
    ribbon[1].info(f"Effective Query: {result.query}")
    ribbon[2].info(f"Tool Calls: {len(result.tool_trace)}")

    body_left, body_right = st.columns([1.35, 0.9], gap="large")
    with body_left:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-kicker">Digest Report</div>
                <div class="section-title">结构化研究摘要</div>
                <div class="section-copy">用于快速筛选候选论文，也适合直接复制到日报或周报里。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(result.markdown)

    with body_right:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-kicker">Execution Trace</div>
                <div class="section-title">调用轨迹</div>
                <div class="section-copy">帮助你观察 agent 是怎么检索、筛选和总结论文的。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if result.tool_trace:
            st.code("\n".join(result.tool_trace), language="text")
        else:
            st.info("本次没有记录到额外工具调用。")

    st.write("")
    st.markdown(
        """
        <div class="section-card">
            <div class="section-kicker">Paper Shelf</div>
            <div class="section-title">保留论文详情</div>
            <div class="section-copy">适合继续阅读、核验来源或挑选后续要加入长期订阅的主题。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    for index, paper in enumerate(result.papers, start=1):
        with st.expander(f"{index}. {paper.title}", expanded=index == 1):
            meta_cols = st.columns(2)
            meta_cols[0].write(f"作者：{', '.join(paper.authors) if paper.authors else '未知'}")
            meta_cols[1].write(f"发布时间：{paper.published or '未知'}")
            st.write(f"arXiv：{paper.entry_url}")
            st.write(f"PDF：{paper.pdf_url}")
            st.write(f"摘要：{paper.summary}")
            st.write(f"一句话总结：{paper.tldr or '暂无'}")
            st.write(f"核心问题：{paper.problem or '暂无'}")
            st.write(f"方法：{paper.method or '暂无'}")
            st.write(f"结果：{paper.results or '暂无'}")


def _format_recipient_text(subscription, channel: str) -> str:
    values = [item.target for item in subscription.recipients if item.channel == channel and item.enabled]
    return "\n".join(values)


def _subscription_table_rows(subscriptions) -> list[dict[str, object]]:
    rows = []
    for item in subscriptions:
        rows.append(
            {
                "ID": item.id,
                "名称": item.name,
                "状态": "启用" if item.enabled else "停用",
                "关键词数": len(item.keywords),
                "接收端数": len(item.recipients),
                "时间": f"{item.schedule_hour:02d}:{item.schedule_minute:02d}",
                "时区": item.timezone,
                "去重天数": item.dedupe_days,
            }
        )
    return rows


def _run_table_rows(runs) -> list[dict[str, object]]:
    rows = []
    for run in runs:
        rows.append(
            {
                "Run ID": run.id,
                "模式": run.trigger_mode,
                "状态": run.status,
                "论文数": run.papers_count,
                "计划日期": str(run.scheduled_for_date or ""),
                "开始时间": run.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                "错误": run.error_message or "",
            }
        )
    return rows


def _render_subscription_tab(subscription_service: SubscriptionService, runtime_api_key: str) -> None:
    subscriptions = subscription_service.list_subscriptions()
    selected_id = None
    if subscriptions:
        options = {f"#{item.id} · {item.name}": item.id for item in subscriptions}
        selected_label = st.selectbox(
            "选择要管理的订阅",
            options=list(options.keys()),
            index=0,
            help="可以查看详情、更新配置、手动试跑或删除订阅。",
        )
        selected_id = options[selected_label]
        selected_subscription = next(item for item in subscriptions if item.id == selected_id)
    else:
        selected_subscription = None

    top_left, top_right = st.columns([1.1, 1], gap="large")

    with top_left:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-kicker">Create Subscription</div>
                <div class="section-title">把高价值检索沉淀成长期订阅</div>
                <div class="section-copy">
                    推荐的工作流是：先在检索台里找到稳定有效的方向，再把它配置成每天自动运行的订阅。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        with st.form("create_subscription_form", clear_on_submit=True):
            name = st.text_input("订阅名称", placeholder="例如：多智能体系统日报")
            query = st.text_input("完整 Query（可选）", placeholder='例如：cat:cs.AI AND all:"multi-agent"')
            keywords = st.text_area(
                "关键词（当 Query 为空时生效）",
                height=120,
                placeholder="multi-agent systems\nreasoning\nrag",
                help="一行一个关键词；系统会自动构造 arXiv 查询语句。",
            )
            focus = st.text_area("研究关键词 / Focus", value=DEFAULT_FOCUS, height=120)
            config_cols = st.columns(4)
            top_k = config_cols[0].number_input("Top K", min_value=1, max_value=20, value=5)
            max_results = config_cols[1].number_input("Max Results", min_value=5, max_value=100, value=50)
            schedule_hour = config_cols[2].number_input("小时", min_value=0, max_value=23, value=8)
            schedule_minute = config_cols[3].number_input("分钟", min_value=0, max_value=59, value=0)
            config_cols2 = st.columns(2)
            timezone = config_cols2[0].text_input("时区", value=DEFAULT_TIMEZONE)
            dedupe_days = config_cols2[1].number_input("跨天去重天数", min_value=1, max_value=30, value=1)
            enabled = st.toggle("创建后立即启用", value=True)
            email_text = st.text_area(
                "邮箱接收人",
                height=110,
                placeholder="alice@example.com\nbob@example.com",
            )
            feishu_text = st.text_area(
                "飞书 Webhook",
                height=110,
                placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/...",
            )
            create_clicked = st.form_submit_button("创建订阅", use_container_width=True)

        if create_clicked:
            try:
                payload = SubscriptionCreateRequest(
                    name=name,
                    query=query.strip() or None,
                    keywords=_parse_multiline(keywords),
                    focus=focus,
                    top_k=int(top_k),
                    max_results=int(max_results),
                    schedule_hour=int(schedule_hour),
                    schedule_minute=int(schedule_minute),
                    timezone=timezone.strip() or DEFAULT_TIMEZONE,
                    dedupe_days=int(dedupe_days),
                    enabled=enabled,
                    recipients=_build_recipient_payloads(email_text, feishu_text),
                )
                created = subscription_service.create_subscription(payload)
                st.success(f"订阅已创建：#{created.id} {created.name}")
                st.rerun()
            except Exception as exc:
                st.error(f"创建失败：{exc}")

    with top_right:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-kicker">Inventory</div>
                <div class="section-title">现有订阅一览</div>
                <div class="section-copy">
                    先看整体排班，再决定要调整、停用还是删除哪一条订阅。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        rows = _subscription_table_rows(subscriptions)
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("还没有任何订阅。先在左侧创建第一条。")

    st.write("")
    st.markdown(
        """
        <div class="section-card">
            <div class="section-kicker">Manage Subscription</div>
            <div class="section-title">编辑、试跑与查看历史</div>
            <div class="section-copy">
                为了降低误操作，这里只针对当前选中的一条订阅进行操作；每次改动都能立即落到 SQLite。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    if not selected_subscription:
        st.info("创建至少一条订阅后，这里会显示编辑与试跑面板。")
        return

    detail_cols = st.columns([1.08, 0.92], gap="large")

    with detail_cols[0]:
        with st.form(f"update_subscription_form_{selected_subscription.id}", clear_on_submit=False):
            edit_name = st.text_input("订阅名称", value=selected_subscription.name)
            edit_query = st.text_input("完整 Query（可选）", value=selected_subscription.query or "")
            edit_keywords = st.text_area(
                "关键词（当 Query 为空时生效）",
                value="\n".join(selected_subscription.keywords),
                height=120,
            )
            edit_focus = st.text_area("研究关键词 / Focus", value=selected_subscription.focus, height=120)
            edit_cols = st.columns(4)
            edit_top_k = edit_cols[0].number_input(
                "Top K",
                min_value=1,
                max_value=20,
                value=selected_subscription.top_k,
                key=f"edit_top_k_{selected_subscription.id}",
            )
            edit_max_results = edit_cols[1].number_input(
                "Max Results",
                min_value=5,
                max_value=100,
                value=selected_subscription.max_results,
                key=f"edit_max_results_{selected_subscription.id}",
            )
            edit_hour = edit_cols[2].number_input(
                "小时",
                min_value=0,
                max_value=23,
                value=selected_subscription.schedule_hour,
                key=f"edit_hour_{selected_subscription.id}",
            )
            edit_minute = edit_cols[3].number_input(
                "分钟",
                min_value=0,
                max_value=59,
                value=selected_subscription.schedule_minute,
                key=f"edit_minute_{selected_subscription.id}",
            )
            edit_cols2 = st.columns(2)
            edit_timezone = edit_cols2[0].text_input("时区", value=selected_subscription.timezone)
            edit_dedupe = edit_cols2[1].number_input(
                "跨天去重天数",
                min_value=1,
                max_value=30,
                value=selected_subscription.dedupe_days,
                key=f"edit_dedupe_{selected_subscription.id}",
            )
            edit_enabled = st.toggle(
                "启用该订阅",
                value=selected_subscription.enabled,
                key=f"edit_enabled_{selected_subscription.id}",
            )
            edit_email = st.text_area(
                "邮箱接收人",
                value=_format_recipient_text(selected_subscription, "email"),
                height=100,
                key=f"edit_email_{selected_subscription.id}",
            )
            edit_feishu = st.text_area(
                "飞书 Webhook",
                value=_format_recipient_text(selected_subscription, "feishu"),
                height=100,
                key=f"edit_feishu_{selected_subscription.id}",
            )
            save_clicked = st.form_submit_button("保存改动", use_container_width=True)

        if save_clicked:
            try:
                updated = subscription_service.update_subscription(
                    selected_subscription.id,
                    SubscriptionUpdateRequest(
                        name=edit_name,
                        query=edit_query,
                        keywords=_parse_multiline(edit_keywords),
                        focus=edit_focus,
                        top_k=int(edit_top_k),
                        max_results=int(edit_max_results),
                        schedule_hour=int(edit_hour),
                        schedule_minute=int(edit_minute),
                        timezone=edit_timezone.strip() or DEFAULT_TIMEZONE,
                        dedupe_days=int(edit_dedupe),
                        enabled=edit_enabled,
                        recipients=_build_recipient_payloads(edit_email, edit_feishu),
                    ),
                )
                st.success(f"已更新订阅：#{updated.id} {updated.name}")
                st.rerun()
            except Exception as exc:
                st.error(f"更新失败：{exc}")

    with detail_cols[1]:
        st.markdown(
            f"""
            <div class="micro-card">
                <div class="micro-label">Selected</div>
                <div class="micro-title">#{selected_subscription.id} · {selected_subscription.name}</div>
                <div class="micro-meta">Effective Query：{selected_subscription.effective_query}</div>
            </div>
            <div class="micro-card">
                <div class="micro-label">Delivery</div>
                <div class="micro-title">{len(selected_subscription.recipients)} 个接收端</div>
                <div class="micro-meta">其中包含邮箱与飞书 webhook，执行结果会记录在运行历史中。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_cols = st.columns(2)
        if action_cols[0].button("手动试跑并发送", use_container_width=True, key=f"run_notify_{selected_subscription.id}"):
            if not runtime_api_key:
                st.error("手动试跑前请先填写 DashScope API Key。")
            else:
                try:
                    result = _build_runtime_service(runtime_api_key).run_subscription(
                        selected_subscription.id,
                        notify=True,
                        api_key=runtime_api_key,
                    )
                    st.success(
                        f"试跑完成：保留 {len(result.papers)} 篇，成功通道 {', '.join(result.notified_channels) or '无'}"
                    )
                except Exception as exc:
                    st.error(f"试跑失败：{exc}")

        if action_cols[1].button("手动试跑不发送", use_container_width=True, key=f"run_dry_{selected_subscription.id}"):
            if not runtime_api_key:
                st.error("手动试跑前请先填写 DashScope API Key。")
            else:
                try:
                    result = _build_runtime_service(runtime_api_key).run_subscription(
                        selected_subscription.id,
                        notify=False,
                        api_key=runtime_api_key,
                    )
                    st.success(f"Dry run 完成：保留 {len(result.papers)} 篇论文。")
                except Exception as exc:
                    st.error(f"Dry run 失败：{exc}")

        delete_confirmed = st.checkbox(
            "我确认要删除这条订阅",
            value=False,
            key=f"delete_confirm_{selected_subscription.id}",
        )

        if st.button(
            "删除当前订阅",
            type="secondary",
            use_container_width=True,
            key=f"delete_{selected_subscription.id}",
        ):
            if not delete_confirmed:
                st.warning("请先勾选删除确认。")
            else:
                try:
                    subscription_service.delete_subscription(selected_subscription.id)
                    st.success(f"已删除订阅 #{selected_subscription.id}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"删除失败：{exc}")

        runs = subscription_service.list_runs(selected_subscription.id)
        st.write("")
        st.markdown("#### 最近执行记录")
        if runs:
            st.dataframe(_run_table_rows(runs), use_container_width=True, hide_index=True)
        else:
            st.info("这条订阅还没有执行记录。")


def main():
    init_db()
    settings = get_settings()
    subscription_service = SubscriptionService(settings)

    st.set_page_config(page_title="arXiv Research Agent", page_icon="AR", layout="wide")
    _inject_styles()

    subscriptions = subscription_service.list_subscriptions()
    recipient_count = sum(len(item.recipients) for item in subscriptions)
    enabled_count = len([item for item in subscriptions if item.enabled])

    runtime_api_key = _render_sidebar(settings, subscriptions)
    _render_hero(
        subscription_count=len(subscriptions),
        enabled_count=enabled_count,
        recipient_count=recipient_count,
        scan_minutes=settings.scheduler_scan_interval_minutes,
    )
    st.write("")

    tab_search, tab_subscriptions = st.tabs(["Research Lab", "Subscription Console"])
    with tab_search:
        _render_search_tab(runtime_api_key)
    with tab_subscriptions:
        _render_subscription_tab(subscription_service, runtime_api_key)


if __name__ == "__main__":
    main()

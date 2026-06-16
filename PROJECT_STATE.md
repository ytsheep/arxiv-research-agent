# PROJECT_STATE.md

# arXiv 论文助手 Agent 项目状态文档

## 1. 当前项目状态

项目当前处于：

```text
阶段：Phase 11 规划中，Multi-Agent Workflow + Redis Cache 待实现
状态：开发中
版本：v0.11.0-planned
```

---

## 2. 已确认的产品方向

项目是一个基于聊天界面的 arXiv 论文助手 Agent。

核心能力：

```text
1. 聊天式论文检索 ✅ Phase 1
2. arXiv 候选论文筛选 ✅ Phase 1
3. 论文卡片展示 ✅ Phase 1
4. 一键收藏 PDF 到本地库 ✅ Phase 2
5. 一键全文解析并生成中文报告 ✅ Phase 3
6. 本地论文库 CRUD ✅ Phase 2
7. 解析文档查看 / 删除 / 重新生成 ✅ Phase 3
8. 每日论文订阅推送 ✅ Phase 4
9. 邮箱 / 飞书推送 ✅ Phase 4
10. 任务流程可观测性查询 ✅ Phase 5
11. Trace 持久化（数据库） ✅ Phase 5
12. TraceTimeline 可视化组件 ✅ Phase 5
13. LLM 集成（卡片摘要 + 精读报告） ✅ Phase 5
14. 用户设置页面 ✅ Phase 5
15. camelCase/snake_case 统一转换层 ✅ Phase 6
16. 多 LLM Provider 支持 (DeepSeek / Qwen / OpenAI) ✅ Phase 6
17. Embedding Rerank (语义匹配) ✅ Phase 6
18. DeepSeek V4 Flash 集成 ✅ Phase 6
19. Tool Registry (5 工具注册, 权限/白名单) ✅ Phase 7
20. Controlled ReAct Agent (LLM 驱动工具选择) ✅ Phase 7
21. Skill Registry (Skill-as-Tool 模式) ✅ Phase 7
22. MCP Server (JSON-RPC over stdio) ✅ Phase 7
23. Trace 推理摘要 (reasoning_summary) ✅ Phase 7
24. LangGraph StateGraph 编排层 ✅ Phase 8
25. Four-layer Memory System ✅ Phase 9
26. Research Workflow Agent Expansion (7 Skills, 21 Agent-callable capabilities, Intent Router, Query Rewrite) ✅ Phase 10
27. Multi-Agent Workflow + Redis Cache 设计文档 ✅ Phase 11 planning
```

---

## 3. 已完成文档

| 文档 | 状态 | 说明 |
|---|---|---|
| PRD.md | 已完成 | 定义产品需求、功能边界、验收标准 |
| ARCH.md | 已完成 | 定义技术架构、模块划分、数据流、API |
| PROJECT_STATE.md | 已完成 | 记录项目状态和开发计划 |
| claude.md | 已完成 | 定义 Claude 协作规则和编码约定 |

---

## 4. Phase 1: 聊天论文检索 - 已完成

### 4.1 已完成任务

```text
[x] 初始化前端 Vue3 项目
[x] 初始化后端 FastAPI 项目
[x] 实现基础页面布局 (AppLayout + SideNav)
[x] 实现聊天页面 (ChatView + ChatWindow + MessageBubble + ChatInput)
[x] 实现 POST /api/chat
[x] 实现 intent.classify (关键词规则兜底)
[x] 实现 query.normalize
[x] 实现 arxiv.search (arXiv Atom API)
[x] 实现 paper.rerank (关键词+时效性评分)
[x] 实现 paper.generate_card_summary (摘要提取)
[x] 实现论文卡片组件 PaperCard.vue
[x] 实现基础 trace 记录 (in-memory)
[x] 实现前端 dark theme
[x] 实现 Element Plus UI 组件库
```

---

## 5. Phase 2: 收藏论文和本地论文库 - 已完成

### 5.1 已完成任务

```text
[x] 实现 POST /api/papers/{arxiv_id}/collect (含 camelCase 转换)
[x] 实现 PDF 下载 (httpx → arXiv)
[x] 实现 PDF 文本提取 (PyMuPDF/fitz)
[x] 实现 metadata.json 保存
[x] 实现 papers 表 CRUD (SQLAlchemy)
[x] 实现 paper_files 表
[x] 实现本地文件目录结构 (paper_library/papers/{arxiv_id}/)
[x] 实现 GET /api/library/papers (搜索+分页)
[x] 实现 GET /api/library/papers/{arxiv_id}
[x] 实现 DELETE /api/library/papers/{arxiv_id} (soft delete)
[x] 实现 LibraryView.vue (论文列表+搜索+删除)
[x] 收藏过程记录 trace (with steps)
[x] ChatWindow 收藏按钮接入 API
```

---

## 6. Phase 3: 论文全文解析和报告查看 - 已完成

### 6.1 已完成任务

```text
[x] 实现 POST /api/papers/{arxiv_id}/parse (完整流程)
[x] 实现 pdf.parse_full_text (PyMuPDF 章节提取)
[x] 实现 parsed.md 生成 (结构化 Markdown)
[x] 实现 paper.generate_deep_report (模板化中文报告)
[x] 实现 report.md 生成 (10 章节)
[x] 实现 ReportViewer.vue (Markdown 渲染 + 操作按钮)
[x] 实现 GET /api/library/papers/{arxiv_id}/report
[x] 实现 DELETE /api/library/papers/{arxiv_id}/report
[x] 实现 POST /api/library/papers/{arxiv_id}/report/regenerate
[x] 解析过程记录 trace (5 steps)
[x] LibraryTool.update_after_parse (status→parsed)
[x] 前端解析按钮接入 (ChatWindow + LibraryView)
[x] 前端报告路由 /report/:arxivId
```

---

## 7. Phase 4: 每日订阅和推送 - 已完成

### 7.1 已完成任务

```text
[x] 实现 subscriptions 表 CRUD API (POST/GET/PUT/DELETE)
[x] 实现 subscription_runs 表记录
[x] 实现 APScheduler 每日任务调度
[x] 实现 subscription.run 流程 (搜索→筛选→入库→通知)
[x] 实现 notify.send_email (SMTP + HTML)
[x] 实现 notify.send_feishu (Webhook 卡片消息)
[x] 实现 SubscriptionView.vue 完整 UI (卡片列表+表单对话框)
[x] 实现 立即运行 (run-now) 功能
[x] 订阅运行记录 trace
[x] 自动入藏论文 (auto-collect)
[x] main.py 集成 scheduler 启动/关闭
```

---

## 8. Phase 5: Trace 持久化 / LLM 集成 / 设置页面 - 已完成

### 8.1 已完成任务

```text
[x] Trace 持久化到 SQLite 数据库 (Task + TaskStep 表)
[x] Trace query API 支持筛选 (keyword/task_type/status/page)
[x] Trace get API 返回完整 steps
[x] TraceTool.log_step() / complete() 改为 async，写数据库
[x] 所有调用方 (orchestrator/paper_service/subscription_job) 更新 await
[x] TraceTimeline.vue 可视化组件 (步骤时间线、状态图标、输入输出、错误展示)
[x] TraceView.vue 完整 UI (筛选器、展开/收起、分页)
[x] LLM Client 集成 (OpenAI-compatible API, JSON mode)
[x] ReportTool 使用 LLM 生成卡片摘要 (fallback 到正则)
[x] ReportTool 使用 LLM 生成精读报告 (fallback 到模板)
[x] Prompts 管理 (CARD_SUMMARY_SYSTEM, DEEP_REPORT_SYSTEM, etc.)
[x] Settings API (GET/PUT /api/settings/preferences, 合并默认值)
[x] SettingsView.vue 完整 UI (搜索默认值、偏好设置、AI 配置展示)
[x] settingsStore.ts 状态管理
[x] UserPreference 数据库模型
```

### 8.2 新增/重写文件 (Phase 5)

```
backend/
  app/
    tools/
      trace_tool.py           — 重写：in-memory → SQLAlchemy 持久化
      llm_client.py            — 新增：OpenAI-compatible API 客户端
      report_tool.py           — 更新：LLM 增强 + 正则 fallback
    agent/
      prompts.py               — 新增：Prompt 模板管理
    services/
      trace_service.py         — 更新：async query/get
    api/
      traces.py                — 更新：await service calls
      settings.py              — 重写：完整 CRUD

frontend/
  src/
    components/trace/
      TraceTimeline.vue        — 新增：步骤时间线可视化
    views/
      TraceView.vue            — 重写：完整筛选+展开+分页
      SettingsView.vue         — 重写：完整偏好设置表单
    stores/
      settingsStore.ts         — 新增：设置状态管理
```

### 8.3 验收状态

```text
[x] 聊天请求 → trace 写入 DB → 重启后端 → trace 仍可查询
[x] TraceView 可按 task_type/status/keyword 筛选
[x] TraceTimeline 展示步骤名称、状态图标、输入/输出、错误信息
[x] LLM API Key 未配置时自动降级到正则/模板
[x] LLM API Key 配置后卡片摘要和精读报告质量提升
[x] SettingsView 可编辑并保存用户偏好
[x] 偏好设置持久化到数据库，重启不丢失
[x] 前端 type-check 通过 (vue-tsc --noEmit)
```

---

## 9. Phase 6: 深度完善 - 已完成

### 9.1 已完成任务

```text
[x] camelCase/snake_case 统一转换层 (formatKeys.ts + http.ts interceptor)
[x] 多 LLM Provider 支持 (openai / deepseek / qwen / openai-compatible)
[x] Embedding Rerank (LLM embedding API + TF-IDF fallback)
[x] RerankTool 重写为 async，集成语义匹配
[x] DeepSeek V4 Flash 适配 (base URL + model name)
[x] Settings API 返回真实 LLM 配置状态
[x] SettingsView 展示 Provider + Model + Status
```

### 9.2 新增/重写文件 (Phase 6)

```
backend/
  app/
    tools/
      embedding_tool.py       — 新增：LLM embedding + TF-IDF fallback
      llm_client.py           — 重写：多 provider 架构 + embed() 方法
      rerank_tool.py          — 重写：async + 语义匹配 + 评分权重调整
    core/
      config.py               — 更新：新增 llm_provider, llm_base_url

frontend/
  src/
    utils/
      formatKeys.ts           — 更新：新增 camelToSnake + 扩展映射表
    api/
      http.ts                 — 更新：request interceptor 自动转换
    views/
      SettingsView.vue        — 更新：展示 LLM Provider/Model/Status
```

### 9.3 LLM 配置状态

```text
Provider: deepseek
Model: deepseek-v4-flash
API Key: 已配置
LLM 增强: 可用（卡片摘要已使用 LLM）
Embedding: 本地 BGE-M3 (BAAI/bge-m3, 1024-dim)
Rerank: 语义=BGE-M3, 摘要=LLM
```

---

## 10. Phase 7: Controlled ReAct Agent 架构升级 - 已完成

### 10.1 已完成任务

```text
[x] Tool Registry (tool_registry.py + tool_schemas.py) — 统一工具注册/权限/白名单
[x] ToolDefinition dataclass (name, schema, handler, allowed_intents, permission)
[x] 注册 5 个 read-only 工具 (arxiv_search, paper_rerank, paper_generate_card_summary, library_search_papers, trace_query)
[x] LLM Client 升级 (chat_with_tools + plan_with_tools)
[x] ReAct Agent MVP (react_agent.py) — 受控 ReAct 循环，max_steps=6
[x] AgentState 状态管理 (observations 积累，state_summary 压缩)
[x] Business rule enforcement (搜索阶段禁止全文解析，收藏/解析分离等)
[x] Skill Registry (skill_registry.py) — Skill-as-Tool 模式
[x] paper_search_card_skill — 固定流程包装 (intent→normalize→search→rerank→summary)
[x] trace_diagnosis_skill — 任务诊断 (query→get→diagnose)
[x] Orchestrator 升级 — USE_REACT_AGENT 特性开关，默认 false 保持向后兼容
[x] Trace 模型升级 — TaskStep 新增 reasoning_summary 字段
[x] TraceTool 升级 — log_step/get/query 支持 reasoning_summary
[x] 前端 TraceStep 类型更新 — 新增 reasoningSummary
[x] TraceTimeline 组件升级 — 展示 ReAct reasoning_summary + action + observation
[x] MCP Server — 标准 MCP 协议 (JSON-RPC over stdio)
[x] MCP Tools — arxiv.search_papers, library.search_papers, library.get_report, trace.query, trace.get
[x] MCP Resources — library://paper/{id}/report|metadata|parsed, trace://recent|failed|{id}
[x] MCP Prompts — paper/card_summary_zh, paper/deep_report_zh
[x] 数据库迁移 — task_steps 表新增 reasoning_summary 列
```

### 10.2 新增/修改文件 (Phase 7)

```
backend/
  app/
    agent/
      tool_schemas.py              — 新增：ToolDefinition + OpenAI function schemas
      tool_registry.py             — 新增：ToolRegistry (注册/校验/调用/权限/业务规则)
      bootstrap.py                 — 新增：创建并注册所有工具实例
      react_agent.py               — 新增：Controlled ReAct Agent (max_steps=6, 白名单检查)
      skill_registry.py            — 新增：SkillRegistry (Skill-as-Tool 包装)
      skills/
        __init__.py                — 新增
        paper_search_card_skill.py — 新增：论文搜索固定流程 Skill
        trace_diagnosis_skill.py   — 新增：任务诊断 Skill
      orchestrator.py              — 修改：集成 ReAct Agent，USE_REACT_AGENT 开关
    tools/
      llm_client.py                — 修改：新增 chat_with_tools() + plan_with_tools()
      trace_tool.py                — 修改：log_step/get 支持 reasoning_summary
    models/
      trace.py                     — 修改：TaskStep 新增 reasoning_summary 列
    core/
      config.py                    — 修改：新增 use_react_agent 配置项
  mcp_server/                      — 新增：MCP Server 目录
    server.py                      — MCP Server 入口 (JSON-RPC over stdio)
    tools/
      arxiv_tools.py               — arXiv 搜索工具
      library_tools.py             — 本地论文库工具
      trace_tools.py               — Trace 查询工具
    resources/
      library_resources.py         — library:// paper resources
      trace_resources.py           — trace:// resources
    prompts/
      paper_prompts.py             — paper/ prompt templates

frontend/
  src/
    types/
      trace.ts                     — 修改：TraceStep 新增 reasoningSummary
    utils/
      formatKeys.ts                — 修改：新增 reasoning_summary 映射
    components/trace/
      TraceTimeline.vue            — 修改：展示 ReAct reasoning/action/observation
```

### 10.3 架构变化

```text
升级前：
  Vue3 Frontend → FastAPI → AgentOrchestrator (固定流程)
                              ↓
                           直接调用 Tool

升级后：
  Vue3 Frontend → FastAPI → AgentOrchestrator
                              ├─ 固定流程 (use_react=false, 默认)
                              └─ ReAct Agent (use_react=true)
                                   ↓
                              Tool Registry (白名单/权限/业务规则)
                                   ↓
                              Tool Layer (ArxivTool, RerankTool, ...)
                                   
  MCP Client (Claude/Cursor) → MCP Server (JSON-RPC over stdio)
                                   ↓
                              同一套 Tool/Service 层
```

### 10.4 安全机制

| 机制 | 说明 |
|------|------|
| Tool Registry | 所有工具调用必须通过注册表，白名单校验 |
| Permission Levels | read_only / write_safe / write_dangerous / expensive / external_send |
| Business Rules | 搜索阶段禁止全文解析，收藏/解析分离，删除默认 soft |
| max_steps=6 | ReAct 循环步数上限，防止失控 |
| Trace-first | 每一步记录 reasoning_summary + action + observation |
| 敏感信息保护 | trace 不记录 API Key/webhook 明文/完整 prompt |
| Feature Flag | USE_REACT_AGENT=false 默认，不影响现有功能 |

---

## 11. 已知问题

1. **Embedding**: 已升级为本地 BGE-M3，不再依赖 LLM Provider。首次加载需下载模型 (~2GB)，后续缓存使用。
2. **PDF 解析质量**: 章节识别基于正则，多栏/复杂格式 PDF 可能解析不完整。
3. **arXiv 429 限流**: 短时间内多次请求会被 arXiv 限流，触发 HTTP 429。
4. **Embedding 已升级为本地 BGE-M3**: 不再依赖 LLM Provider 的 embedding API，直接使用本地 BAAI/bge-m3 模型 (1024-dim)，语义匹配质量大幅提升。

---

## 12. 下一步计划

1. **Phase 11 Multi-Agent Workflow**: 支持复合任务 search -> compare -> select_best -> collect -> deep_read
2. **Redis Cache**: 增加 arXiv 搜索缓存、Embedding/Rerank 缓存、Workflow 轻量状态缓存
3. **paper_select_best_skill**: 基于对比结果和用户偏好选择最适合的论文
4. **paper_compare_skill 输入增强**: 支持直接消费 freshly searched papers
5. **前端适配新响应类型**: 前端渲染 deep_read_result, comparison_result, survey_result, memory_profile_result, trace_diagnosis_result
6. **全库问答 RAG**: 基于已收藏论文的全文检索问答
7. **Zotero/Notion 同步**: 论文库导出到第三方工具

---

## 13. MCP Server 使用说明

启动 MCP Server：
```bash
cd backend
python -m mcp_server.server
```

配置 Claude Desktop / Cursor 的 MCP：
```json
{
  "mcpServers": {
    "arxiv-paper-agent": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "backend"
    }
  }
}
```

---

## 14. 如何运行

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npx vite --port 5173
```

### 验证
```bash
# Health check
curl http://localhost:8000/api/health

# Chat (search papers)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"find 2 papers about agents"}'

# View traces
curl http://localhost:8000/api/traces

# View trace detail
curl http://localhost:8000/api/traces/{trace_id}

# Settings
curl http://localhost:8000/api/settings/preferences
```

### LLM 配置 (可选)
在 `backend/.env` 中设置：
```
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxx
LLM_MODEL=deepseek-v4-flash
```
支持的 Provider：`openai` / `deepseek` / `qwen` / `openai-compatible`

---

## 15. Phase 8: LangGraph 状态图编排升级 - 已完成

### 15.1 已完成任务
```text
[x] 新增 LangGraph StateGraph 编排层
[x] 将聊天入口迁移为 FastAPI -> AgentOrchestrator -> LangGraphAgentRunner
[x] 将论文搜索固定流程迁移为固定业务子图
[x] 新增受控 ReAct 子图：plan -> guard -> execute -> observe -> final
[x] 保留 Tool Registry 作为权限校验、schema 管理和执行分发层
[x] 将 paper_search_card_skill 注册为高阶 Skill Tool，ReAct 优先调用 Skill
[x] 接入 LangGraph AsyncSqliteSaver Checkpointer，checkpoint 成为状态事实来源
[x] 新增 TraceProjectionService，从 checkpoint history 投影 TraceTimeline steps
[x] TraceTool 保留为任务索引和旧流程兼容层，不再作为 LangGraph 状态 checkpoint
```

### 15.2 新增/修改文件
```text
backend/app/agent/state.py
backend/app/agent/graph_runner.py
backend/app/agent/orchestrator.py
backend/app/services/trace_projection_service.py
backend/app/services/trace_service.py
backend/app/agent/bootstrap.py
backend/app/agent/tool_registry.py
backend/app/core/config.py
backend/app/schemas/trace.py
backend/main.py
backend/requirements.txt
```

### 15.3 当前架构关系
```text
FastAPI API 层
-> LangGraph StateGraph 编排层
-> 固定业务子图 / ReAct 子图
-> Skill 层
-> Tool Registry
-> Local Tool / MCP Adapter / RAG / DB / 文件系统
-> LangGraph Checkpointer 作为状态事实来源
-> TraceProjection 从 checkpoint history 生成可观测 UI
```

### 15.4 已验证
```text
[x] Python 静态编译通过
[x] general_chat 路径生成 checkpoint history
[x] paper_search 固定业务子图可执行
[x] ReAct fallback 路径可通过 paper_search_card_skill 执行
[x] TraceProjection 可从 checkpoint history 投影步骤
```
 
---

## 16. Phase 9: Four-layer Memory System - Completed

### 16.1 Completed
```text
[x] Added Working Memory fields to PaperAgentState for messages, last papers, long-term memories, and preferences
[x] Added Short-term Memory as session Messages List with token-budget loading
[x] Added tool_call/tool_response group_id pairing and atomic truncation/compaction
[x] Added Long-term Structured Memory updates for preferred_topics and topic_interest_weights
[x] Added Long-term Semantic Memory table for search history, paper metadata, and report chunks
[x] Connected memory to LangGraph chat startup, ReAct prompt context, rerank preferences, and post-run persistence
[x] Added follow-up paper reference handling for previous paper results
[x] Added interest-query inference for requests like "find papers I am interested in"
```

### 16.2 Added/Modified Files
```text
backend/app/models/memory.py
backend/app/services/memory_service.py
backend/app/models/__init__.py
backend/app/db/database.py
backend/app/agent/state.py
backend/app/agent/graph_runner.py
backend/app/services/paper_service.py
backend/app/api/settings.py
```

### 16.3 Current Memory Architecture
```text
Working Memory: LangGraph PaperAgentState
Short-term Memory: chat_messages Messages List by session_id
Long-term Structured Memory: user_preferences, papers, subscriptions, traces
Long-term Semantic Memory: semantic_memories with embedding_json when available and TF-IDF fallback
```

### 16.4 Verified
```text
[x] python -m compileall backend/app
[x] temporary SQLite smoke test for message loading, tool pair truncation, preference update, and semantic retrieval
```

---

## 17. Phase 10: Research Workflow Agent Expansion - 已完成

### 17.1 Status

```text
completed
```

### 17.2 已完成任务

```text
[x] 新增 5 个 Skill 文件: paper_deep_read_skill, paper_compare_skill, literature_survey_skill, interest_recommendation_skill, memory_profile_skill
[x] 注册 trace_diagnosis_skill 到 Tool Registry (之前已实现但未注册)
[x] 新增 9 个 Tool Schema: library_get_paper, library_get_report, paper_collect, paper_parse_full_text, paper_generate_deep_report, semantic_memory_search, user_preference_get, user_preference_update, trace_get
[x] Tool Registry 注册 21 个 Agent 可调用能力 (7 Skill + 14 Atomic Tool)
[x] 权限分层: read_only(11), write_safe(3), expensive(4), external_send(0), write_dangerous(0)
[x] 新增 Intent 关键词规则: paper_deep_read, paper_compare, literature_survey, interest_recommendation, memory_profile, trace_diagnosis
[x] State 新增 11 个字段: original_query, rewritten_query, query_rewrite_source, query_filters, selected_skill, slots, needs_clarification, clarification_question, report_markdown, comparison, survey_markdown
[x] Graph Runner 升级: _refine_intent 二次意图纠正, 新意图路由到 ReAct, fallback plan 覆盖所有意图, clarification 消息处理
[x] _react_final_response_node 根据 intent 返回不同的 response type (deep_read_result, comparison_result, survey_result, memory_profile_result, trace_diagnosis_result)
[x] ChatResponse 新增 metadata 字段, 支持传递 report_markdown/comparison/survey 等扩展数据
[x] Business Rules 新增: literature_survey, paper_compare, interest_recommendation 禁止调用 expensive 工具
[x] paper_deep_read 允许 expensive 工具 (pdf_parse_full_text, paper_generate_deep_report)
[x] 订阅和通知工具未注册到 ReAct Tool Registry (符合安全要求)
```

### 17.3 新增/修改文件

```
backend/app/agent/
  state.py                                    — 新增 11 个 State 字段
  tool_schemas.py                             — 新增 9 个 OpenAI function schema
  tool_registry.py                            — 新增 3 条 Business Rules
  intent_classifier.py                        — 新增 6 组关键词规则 + entity extraction
  bootstrap.py                                — 重写: 6→21 工具注册, 内联 6 个 handler wrapper
  graph_runner.py                             — 更新: _refine_intent, _route_after_intent, _fallback_react_plan, _general_chat_node, _react_observe_node, _react_final_response_node, 5 个新 helper 方法
  skills/
    paper_deep_read_skill.py                  — 新增: 精读论文 Skill (resolve→collect→parse→report)
    paper_compare_skill.py                    — 新增: 论文对比 Skill (LLM + template fallback)
    literature_survey_skill.py                — 新增: 文献综述 Skill (expand→search→survey)
    interest_recommendation_skill.py           — 新增: 兴趣推荐 Skill (preferences→query→search)
    memory_profile_skill.py                   — 新增: 偏好管理 Skill (read/update preferences)

backend/app/schemas/
  chat.py                                     — ChatResponse 新增 metadata: dict 字段
```

### 17.4 Tool Registry 全景 (21 tools)

```
Skills (7):
  paper_search_card_skill          read_only
  paper_deep_read_skill            expensive
  paper_compare_skill              read_only
  literature_survey_skill          read_only
  interest_recommendation_skill    read_only
  memory_profile_skill             write_safe
  trace_diagnosis_skill            read_only

Atomic Tools (14):
  arxiv_search                     read_only
  paper_rerank                     read_only
  paper_generate_card_summary      read_only
  library_search_papers            read_only
  library_get_paper                read_only
  library_get_report               read_only
  semantic_memory_search           read_only
  user_preference_get              read_only
  trace_query                      read_only
  trace_get                        read_only
  paper_collect                    write_safe
  user_preference_update           write_safe
  paper_parse_full_text            expensive
  paper_generate_deep_report       expensive

NOT registered (manual UI only):
  subscription_create/update/run_now
  notify_send_email/send_feishu
```

### 17.5 Intent Routing Flow

```text
用户输入 → classify_intent (keyword规则)
  → _refine_intent (二次纠正: deep_read, compare, survey, memory_profile, trace_diagnosis)
  → _route_after_intent:
    paper_search → fixed pipeline / ReAct (根据 use_react)
    新 intent → ReAct (paper_search_react)
    general_chat → general_chat
    needs_clarification → general_chat (澄清问题)
```

### 17.6 已验证

```text
[x] python -m compileall backend/app — 全部编译通过
[x] Tool Registry 创建 21 个工具全部成功
[x] Graph 结构完整 (14 nodes)
[x] State 字段完整 (43 fields, 含 11 新增)
[x] "find 2 papers about agent memory" → intent=paper_search, skill=paper_search_card_skill ✓
[x] "deep read the second paper" → intent=paper_deep_read, skill=paper_deep_read_skill ✓
[x] Backend health endpoint returns ok
[x] Traces API 返回 18 条 trace
[x] Library API 返回 3 篇论文
[x] Settings API 返回偏好设置
[x] Subscriptions API 正常
[x] 订阅/通知工具未注册到 Tool Registry ✓ (安全要求)
[x] BUSINESS_RULES 禁止 paper_search/literature_survey/paper_compare 调用 expensive 工具 ✓
```

---

## 18. Phase 11: Multi-Agent Workflow + Redis Cache - 已完成

### 18.1 Status

```text
completed
```

### 18.2 目标

在现有 LangGraphAgentRunner、Skill/Tool Registry、Memory、Trace、MCP 基础上，新增一个轻量多 Agent 工作流，用于处理一句话中包含多个依赖动作的复杂科研任务。

目标示例：

```text
帮我找两篇 RAG 相关论文，并且对比两论文的优缺点，最后把好的那篇收藏，并解析
```

期望执行链路：

```text
search_papers
-> compare_papers
-> select_best_paper
-> collect_paper
-> deep_read_paper
-> final_summary
```

### 18.3 设计原则

```text
1. 不删除现有 LangGraphAgentRunner，新增 MultiAgentGraphRunner。
2. 简单任务继续走现有图，复合任务才走多 Agent 图。
3. Supervisor 只规划和调度，不直接调用工具。
4. Executor 只执行单个子任务，不做全局规划，不再嵌套自由 ReAct。
5. Reviewer 只验收任务完成度和输出质量，不调用业务工具。
6. Message Bus 第一版使用 WorkflowState.message_history，不引入 Kafka/RabbitMQ。
7. LangGraph Checkpointer 保存完整 WorkflowState，是状态事实来源。
8. Redis 只做缓存和轻量状态投影，不替代 Checkpointer、SQLite、文件系统。
```

### 18.4 待新增文件

```text
backend/app/agent/
  multi_agent_runner.py
  workflow_state.py
  message_schema.py
  message_bus.py

backend/app/agent/supervisor/
  planner.py
  dispatcher.py
  prompts.py

backend/app/agent/executor/
  executor_agent.py
  execution_map.py
  input_resolver.py

backend/app/agent/reviewer/
  reviewer_agent.py
  completion_checker.py
  final_composer.py

backend/app/services/
  cache_service.py

backend/app/core/
  redis.py
```

### 18.5 待修改文件

```text
backend/app/agent/orchestrator.py
backend/app/agent/bootstrap.py
backend/app/agent/tool_schemas.py
backend/app/agent/skills/paper_compare_skill.py
backend/app/services/trace_projection_service.py
backend/app/core/config.py
backend/requirements.txt
frontend/src/types/trace.ts
frontend/src/components/trace/TraceTimeline.vue
```

### 18.6 新增 Skill

```text
paper_select_best_skill
```

职责：

```text
基于候选论文、论文对比结果、用户长期偏好和用户任务目标，选择最适合的一篇论文。
```

输入：

```text
papers
comparison
user_preferences
user_message
```

输出：

```text
selected_paper
selection_reason
tradeoff_summary
```

要求：

```text
LLM 可用时使用 LLM 判断。
LLM 不可用时使用规则兜底，例如 rerank_score、偏好主题匹配、发布时间、summary/core_problem/method 信息完整度。
```

### 18.7 需要增强的现有 Skill

```text
paper_compare_skill
```

增强要求：

```text
1. 支持 arxiv_ids 输入，用于本地库已有论文对比。
2. 支持 papers 输入，用于刚搜索出来但尚未收藏的论文对比。
3. 本地 report 存在时可补充 report 内容。
4. 本地 report 不存在时，必须能基于 title/abstract/summary/core_problem/method/result 做卡片级对比。
```

### 18.8 Multi-Agent WorkflowState

新增 WorkflowState，用于 Checkpointer 保存完整多 Agent 状态：

```text
trace_id
session_id
workflow_id
user_message
task_plan
current_task_id
task_outputs
pending_tasks
running_tasks
completed_tasks
failed_tasks
message_history
last_review_decision
retry_count
replan_count
user_preferences
long_term_memories
last_papers
selected_paper
final_response
status
error
```

### 18.9 AgentMessage

Agent 间通信使用统一消息结构：

```text
message_id
workflow_id
task_id
sender
receiver
message_type
payload
metadata
timestamp
```

消息类型：

```text
user.request
task.planned
task.assigned
task.result
task.reviewed
workflow.final
workflow.error
```

### 18.10 Redis Cache 范围

只实现三类缓存：

```text
1. arXiv 搜索结果缓存
2. Embedding / Rerank 缓存
3. Workflow 轻量状态缓存
```

不要缓存：

```text
1. 完整 PDF 文件
2. 完整 parsed.md/report.md 大文本
3. 用户偏好事实源
4. 论文库事实源
5. Checkpointer 完整状态
```

### 18.11 Redis Key 设计

```text
arXiv:
  arxiv:search:{hash(normalized_query + candidate_k)}
  TTL: 30 minutes to 6 hours

Embedding:
  embedding:{hash(text)}
  TTL: 7 to 30 days

Rerank:
  rerank:{hash(query + paper_ids + preference_version)}
  TTL: 30 minutes to 2 hours

Workflow:
  workflow:state:{workflow_id}
  TTL: 1 to 24 hours
```

### 18.12 Redis 降级要求

```text
1. Redis 未配置时，所有功能必须照常运行。
2. Redis 连接失败时，只记录 warning，不向前端报错。
3. arXiv cache miss 时走真实 arXiv API。
4. embedding/rerank cache miss 时走原计算逻辑。
5. Workflow cache miss 时从 LangGraph Checkpointer 或 TraceProjection 读取。
6. Embedding 服务不可用时，继续保留 TF-IDF fallback。
```

### 18.13 Claude Code 实现后必须验证

Claude Code 完成代码后必须执行并记录验证结果：

```text
Backend 基础:
  [ ] python -m compileall backend/app
  [ ] 后端在 Redis 未启动时可正常启动
  [ ] 后端在 REDIS_URL 配置后可连接 Redis
  [ ] GET /api/health 正常

现有功能回归:
  [ ] 简单聊天搜索论文正常
  [ ] 收藏论文正常
  [ ] 解析论文正常
  [ ] 本地论文库查询正常
  [ ] 论文报告查看正常
  [ ] Trace 查询和详情正常
  [ ] Settings 正常
  [ ] 订阅任务页面/API 正常

Multi-Agent:
  [ ] 复合请求能生成 task_plan
  [ ] search_papers 输出 papers
  [ ] compare_papers 消费 search_papers 输出
  [ ] select_best_paper 输出 selected_paper
  [ ] collect_paper 消费 selected_paper
  [ ] deep_read_paper 生成 report_markdown 或安全 partial_final
  [ ] Reviewer 在 required_outputs 缺失时不会 finish
  [ ] retry/replan/partial_final 路径可控

Redis:
  [ ] arXiv search cache miss 后写入 Redis
  [ ] 相同 query 第二次命中 arXiv cache
  [ ] embedding 或 rerank cache miss/hit 可观察
  [ ] workflow:state:{workflow_id} 写入并可读取
  [ ] Redis 故障不会中断 Agent 执行

安全:
  [ ] 订阅/通知工具仍不注册到 Agent Tool Registry
  [ ] ToolRegistry 权限校验仍生效
  [ ] Trace 不记录 API Key、飞书 webhook、完整 PDF 正文
```

### 18.14 Phase 11 完成标准

```text
1. 文档中的复合任务示例可以端到端执行，或在某一步失败时返回可解释 partial_final。
2. Trace 页面可以看到多 Agent 的 plan、assigned、result、review、final 事件。
3. Redis 三类缓存均有命中/未命中的可观测信息。
4. Redis 不可用时，系统保持可运行。
5. 所有 Phase 1-10 核心功能不回退。
```
## 19. Lightweight Evaluation Suite - Completed

### 19.1 Scope

[x] Intent recognition and Skill/Tool dispatch evaluation
[x] arXiv retrieval Recall@3 evaluation
[x] Local PDF parse accuracy evaluation
[x] Per-run latency and provider-reported LLM token usage

### 19.2 Test Data

[x] 60 Agent routing and dispatch cases, including ambiguous and abnormal requests
[x] 40 arXiv retrieval cases
[x] 30 local PDF parsing cases generated from 3 existing source PDFs

### 19.3 Implementation

[x] Added `backend/evaluation/run_eval.py`
[x] Added `backend/evaluation/generate_pdf_cases.py`
[x] Added JSONL test cases under `backend/evaluation/cases/`
[x] Added JSONL and JSON results under `backend/evaluation/outputs/`
[x] Added provider-reported token usage accumulation to `LLMClient`
[x] Added per-stage LLM token usage attribution
[x] Split Single-Agent and Multi-Agent routing/planning latency and token metrics
[x] PDF evaluation reparses each source PDF before validating generated `parsed.md`

### 19.4 Latest Result

```text
Intent Accuracy:               91.67%
Dispatch Accuracy:             91.67%
Single-Agent Avg Latency:       0.21 ms
Single-Agent Avg Tokens:        0.00
Multi-Agent Avg Latency:     6065.52 ms
Multi-Agent Avg Tokens:      1069.10
Multi-Agent Main Token Stage: supervisor_planning (100%)
Retrieval API Success Rate:   100.00%
Retrieval Recall@3:            42.50%
PDF Parse Accuracy:           100.00%
PDF Avg Document Parse:      1045.74 ms
Total Runs:                   130
Total Tokens:               10691
```

Recall@3 is calculated over successful arXiv API responses. External API
failures are reported separately and do not count as relevance misses.
Agent latency and token metrics cover routing and planning only, not complete
end-to-end workflow execution.

### 19.5 Intent And Dispatch Optimization

[x] Specific compare/deep-read/library intents override generic paper-search matches
[x] Context references resolve paper IDs from `last_papers`
[x] Context comparison fills both arXiv IDs from recent paper results
[x] Local library search maps to the registered `library_search_papers` Tool
[x] ReAct fallback uses strict arguments for compare, deep-read, and library search
[x] Replaced all pure-English Agent evaluation questions with Chinese equivalents

### 19.6 Current Failure Coverage

[x] Ambiguous context comparison can expose missing paper references
[x] Local-library wording can be confused with external paper search
[x] Trace lookup and trace diagnosis boundaries are evaluated separately
[x] Negative preference statements test memory-profile routing
[x] Compound workflows verify all required downstream Skills/Tools are dispatched
[x] Retrieval evaluation retries HTTP 429 and records API success rate separately

### 19.7 PDF Parse Accuracy Fix

[x] Increased PDF test samples from 15 to 30
[x] Removed per-section 5000-character truncation
[x] Removed final-section 10000-character truncation
[x] Removed reference-section 8000-character truncation
[x] Preserved document content before the first detected heading
[x] Prevented duplicate reference content in generated `parsed.md`
[x] Normalized line-break hyphenation and deterministic reading order
[x] Replaced brittle arbitrary-character snippets with normalized 24-token windows

### 19.8 Token Attribution

[x] LLM usage is grouped by execution stage in `usage_by_stage`
[x] Supervisor planning, ReAct planning, card summary, comparison, selection,
    survey, final composition, and deep report calls have stage labels
[x] `chat_json` returns both `content` and compatibility `data`, preventing valid
    Supervisor plans from being discarded before rule fallback

### 19.9 Full-Chain Agent Evaluation

[x] Added `backend/evaluation/run_e2e_agent_eval.py`
[x] Added 3 representative full-chain cases with a 90-second per-case timeout
[x] Full-chain benchmark starts from `AgentOrchestrator.handle_chat()`
[x] Reuses one Orchestrator to avoid repeated client and model initialization
[x] Reports latency, provider token usage, LLM stage usage, and Skill usage

Latest full-chain result:

```text
Single-Agent cases:               2/2 completed
Single-Agent average latency:     39.91 s
Single-Agent average tokens:    2965.50

Multi-Agent cases:                1/1 completed
Multi-Agent average latency:      26.73 s
Multi-Agent average tokens:     3453.00

Overall cases:                    3/3 completed
Overall average latency:          35.52 s
Overall total tokens:             9384
```

Token usage by Skill:

```text
paper_deep_read_skill:           3696
paper_search_card_skill:         2770
paper_compare_skill:              981
ControlledReAct:                  891
Supervisor:                       796
FinalComposer:                    250
```

Full-chain issues found and fixed:

```text
1. ReAct repeated an already-successful deep-read Skill until max_steps.
2. LLM task dependencies such as task_1.papers were not normalized to task_1.
3. Reviewer retry incorrectly routed back to Supervisor planning.
4. Retry counters were reset during replanning, causing unbounded loops.
5. Executor added top_n/candidate_k to Skills that did not accept them.
6. Natural-language topic extraction truncated or replaced valid topics.
7. Multi-Agent memory persistence omitted required trace_id and user_message.
```

Current execution limits:

```text
End-to-end evaluation timeout: 90 seconds per case
Multi-Agent max retries:        1
Multi-Agent max replans:        1
```

Run the full evaluation:

```text
cd backend
python evaluation/run_eval.py --type all
```

Run the full-chain Agent evaluation:

```text
cd backend
python evaluation/run_e2e_agent_eval.py
```

### 19.10 Ten-Case Full-Chain Evaluation

[x] Expanded the full-chain set to 4 Single-Agent and 6 Multi-Agent cases
[x] Multi-Agent cases cover 2-task, 3-task, and 4-task workflows
[x] Each case uses a 90-second timeout
[x] Fixed explicit arXiv-ID comparison being routed to clarification
[x] Preserved Supervisor-resolved topics when invoking the paper search Skill
[x] Preserved cold-start metadata for timeout and failure rows

Latest result:

```text
Single-Agent completion:          4/4 (100%)
Single-Agent average latency:     25.28 s
Single-Agent average tokens:    3032.25

Multi-Agent completion:           3/6 (50%)
Multi-Agent task-count accuracy:  6/6 (100%)
Multi-Agent average latency:      30.05 s
Multi-Agent average tokens:     3589.00

Overall completion:               7/10 (70%)
Overall task-count accuracy:      10/10 (100%)
Overall average latency:          28.15 s
Overall total tokens:             33663

BGE-M3 cold search latency:       46.55 s
BGE-M3 warm search latency:       13.35 s
```

The three incomplete Multi-Agent workflows were planned correctly but their
Chinese-only topics returned zero arXiv candidates. Each search retried once
and then returned a controlled `partial_final`, so dependent compare, select,
or survey tasks could not run.

### 19.11 Long-Running Chat Request Fix

[x] Confirmed `/api/chat` is a synchronous long-running request
[x] Identified the frontend global Axios 30-second timeout as the cause of early failure messages
[x] Added a chat-specific 180-second timeout while preserving the 30-second default for other APIs
[x] Added separate messages for connection failure, server error, and chat timeout
[x] Removed three unused frontend imports that blocked the production build
[x] Verified the frontend remains connected beyond 30 seconds and renders the final Multi-Agent result

Verification:

```text
Original user workflow trace: trace_20260615_134136_7f6841
Original workflow status:      success
Original workflow duration:    79 seconds
Original workflow tasks:       search -> compare -> select best -> deep read

Browser verification trace:    trace_20260615_135622_6768cb
Frontend behavior:             remained waiting after 30 seconds and rendered final response
Frontend production build:     passed
```

### 19.12 BGE-M3 Startup Warmup And SSE Progress

[x] BGE-M3 now loads and runs one embedding inference during FastAPI lifespan startup
[x] Added embedding runtime states: not_loaded, loading, ready, degraded, disabled
[x] BGE-M3 warmup failure keeps the backend available through the existing TF-IDF fallback
[x] `/api/health` now reports embedding model status and warmup duration
[x] Added asynchronous chat task submission while preserving synchronous `/api/chat`
[x] Added SSE progress streaming backed by real LangGraph node state changes
[x] Added 15-second SSE heartbeat events for long-running Agent Skills
[x] Added task result lookup and in-process Last-Event-ID replay support
[x] Frontend now updates one streaming Assistant message with workflow stages
[x] Final SSE event replaces the streaming message with the final response and paper cards

New APIs:

```text
POST /api/chat/tasks
GET  /api/chat/tasks/{trace_id}/events
GET  /api/chat/tasks/{trace_id}/result
```

Latest verification:

```text
BGE-M3 startup warmup:          ready in 29.88 seconds
First request BGE cold load:    removed from user request path

Multi-Agent SSE trace:          trace_20260615_143233_bbd899
Multi-Agent workflow:           search -> compare
SSE stage events:               13
Empty task events:              0
Final SSE event:                workflow.completed
Final papers:                   2

Sync API compatibility trace:   trace_20260615_143320_4ad17e
Sync API result:                comparison_result, success
Frontend stream trace:          trace_20260615_143348_faa21b
Frontend production build:      passed
```

Current SSE implementation uses a bounded in-process event history and is
appropriate for the current single-worker interview deployment. LangGraph
Checkpointer remains the durable workflow state source. A future multi-worker
deployment should replace the real-time event bus with Redis Pub/Sub or Redis
Streams while keeping the same SSE API contract.

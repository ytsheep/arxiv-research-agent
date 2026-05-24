# PROJECT_STATE.md

# arXiv 论文助手 Agent 项目状态文档

## 1. 当前项目状态

项目当前处于：

```text
阶段：Phase 6 完成，架构升级完成
状态：开发中
版本：v0.7.0
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
Embedding: 降级到 TF-IDF（DeepSeek 不支持 /embeddings API）
Rerank: 语义=TF-IDF, 摘要=LLM
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

1. **Semantic Embedding**: DeepSeek 不支持 /embeddings API，rerank 使用 TF-IDF（效果仍优于纯关键词）。切换到 OpenAI 可启用 Embedding API。
2. **PDF 解析质量**: 章节识别基于正则，多栏/复杂格式 PDF 可能解析不完整。
3. **arXiv 429 限流**: 短时间内多次请求会被 arXiv 限流，触发 HTTP 429。

---

## 12. 下一步计划

1. **启用 ReAct Agent**: 设置 `USE_REACT_AGENT=true` 测试 ReAct 路径
2. **注册更多工具**: 将 write_safe/expensive 工具注册到 Tool Registry（第二批）
3. **全库问答 RAG**: 基于已收藏论文的全文检索问答
4. **多论文综述生成**: 基于多篇相关论文自动生成综述
5. **Zotero/Notion 同步**: 论文库导出到第三方工具

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

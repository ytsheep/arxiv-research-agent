# PROJECT_STATE.md

# arXiv 论文助手 Agent 项目状态文档

## 1. 当前项目状态

项目当前处于：

```text
阶段：Phase 5 完成，Phase 6 完善中
状态：开发中
版本：v0.6.0
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

## 10. 已知问题

1. **Semantic Embedding**: DeepSeek 不支持 /embeddings API，rerank 使用 TF-IDF（效果仍优于纯关键词）。切换到 OpenAI 可启用 Embedding API。
2. **PDF 解析质量**: 章节识别基于正则，多栏/复杂格式 PDF 可能解析不完整。
3. **arXiv 429 限流**: 短时间内多次请求会被 arXiv 限流，触发 HTTP 429。

---

## 11. 下一步计划

1. **全库问答 RAG**: 基于已收藏论文的全文检索问答
2. **多论文综述生成**: 基于多篇相关论文自动生成综述
3. **Zotero/Notion 同步**: 论文库导出到第三方工具
4. **Anthropic Claude 支持**: 非 OpenAI-compatible 格式适配

---

## 11. 如何运行

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

# ARCH.md

# arXiv 论文助手 Agent 项目架构文档

## 1. 技术栈

### 1.1 前端

前端采用：

```text
Vue 3
Vite
TypeScript
Vue Router
Pinia
Element Plus 或 Naive UI
Markdown 渲染组件
Axios
WebSocket 或轮询
```

推荐：

```text
Vue 3 + Vite + TypeScript + Pinia + Vue Router + Element Plus
```

### 1.2 后端

后端推荐：

```text
Python
FastAPI
Pydantic
SQLAlchemy
SQLite，MVP 阶段
PostgreSQL，正式阶段
APScheduler，MVP 定时任务
Celery + Redis，正式异步任务
```

### 1.3 AI / Agent 层

```text
小模型意图识别
关键词规则兜底
LLM 论文卡片摘要
LLM 论文全文精读报告
Embedding 语义匹配
Rerank 候选论文
```

### 1.4 外部服务

```text
arXiv API
邮箱 SMTP / 邮件 API
飞书群机器人 webhook
PDF 解析库
Embedding 服务
LLM 服务
```

### 1.5 存储

MVP：

```text
SQLite
本地文件系统
```

正式版：

```text
PostgreSQL
pgvector
对象存储，可选
Redis
```

---

## 2. 系统总体架构

```text
Vue3 前端
  ↓
FastAPI 后端 API
  ↓
Agent Orchestrator
  ↓
Tool Layer
  ├── Intent Tool
  ├── arXiv Tool
  ├── Rerank Tool
  ├── PDF Tool
  ├── Report Tool
  ├── Library Tool
  ├── Subscription Tool
  ├── Notify Tool
  └── Trace Tool
  ↓
Data Layer
  ├── SQLite / PostgreSQL
  ├── Local Paper Files
  ├── Parsed Markdown
  ├── Report Markdown
  └── Trace Logs
```

---

## 3. 前端架构

### 3.1 前端目录结构

```text
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  index.html

  src/
    main.ts
    App.vue

    router/
      index.ts

    stores/
      chatStore.ts
      libraryStore.ts
      subscriptionStore.ts
      traceStore.ts
      settingsStore.ts

    api/
      http.ts
      chatApi.ts
      paperApi.ts
      libraryApi.ts
      subscriptionApi.ts
      traceApi.ts
      settingsApi.ts

    views/
      ChatView.vue
      LibraryView.vue
      SubscriptionView.vue
      TraceView.vue
      SettingsView.vue

    components/
      layout/
        AppLayout.vue
        SideNav.vue
        TopBar.vue

      chat/
        ChatWindow.vue
        ChatInput.vue
        MessageBubble.vue
        PaperCard.vue
        TaskProgress.vue

      library/
        PaperTable.vue
        PaperDetailDrawer.vue
        ReportViewer.vue
        TagFilter.vue

      subscription/
        SubscriptionTable.vue
        SubscriptionForm.vue
        SubscriptionRunList.vue

      trace/
        TraceTable.vue
        TraceDetail.vue
        TraceTimeline.vue
        TraceFilter.vue

      common/
        MarkdownViewer.vue
        ConfirmDialog.vue
        LoadingState.vue
        EmptyState.vue

    types/
      chat.ts
      paper.ts
      subscription.ts
      trace.ts
      settings.ts

    utils/
      formatTime.ts
      markdown.ts
      validators.ts
```

---

## 4. 后端架构

### 4.1 后端目录结构

```text
backend/
  main.py

  app/
    api/
      chat.py
      papers.py
      library.py
      subscriptions.py
      traces.py
      settings.py

    core/
      config.py
      security.py
      logging.py

    agent/
      orchestrator.py
      intent_classifier.py
      query_normalizer.py
      prompts.py

    tools/
      arxiv_tool.py
      rerank_tool.py
      pdf_tool.py
      report_tool.py
      library_tool.py
      subscription_tool.py
      notify_tool.py
      trace_tool.py

    services/
      chat_service.py
      paper_service.py
      library_service.py
      subscription_service.py
      trace_service.py
      settings_service.py

    models/
      paper.py
      subscription.py
      trace.py
      settings.py

    schemas/
      chat.py
      paper.py
      subscription.py
      trace.py
      settings.py

    db/
      database.py
      migrations/

    jobs/
      scheduler.py
      daily_subscription_job.py

    storage/
      file_manager.py

  data/
    library.db
    paper_library/
      papers/
```

---

## 5. 前后端页面路由

### 5.1 前端路由

```text
/                     → ChatView
/library              → LibraryView
/subscriptions        → SubscriptionView
/traces               → TraceView
/settings             → SettingsView
```

---

## 6. 后端 API 设计

### 6.1 聊天 API

```http
POST /api/chat
```

请求：

```json
{
  "session_id": "session_001",
  "message": "给我找2篇关于agnet的论文"
}
```

响应：

```json
{
  "type": "paper_search_result",
  "trace_id": "trace_001",
  "message": "找到 2 篇相关论文",
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Case-Grounded Evidence Verification",
      "authors": ["Author A", "Author B"],
      "published_date": "2026-04-10",
      "categories": ["cs.CL"],
      "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
      "pdf_url": "https://arxiv.org/pdf/2604.09537v1",
      "summary": "本文提出...",
      "core_problem": "现有...",
      "method": "提出...",
      "result": "实验显示...",
      "summary_source": "abstract_intro",
      "actions": ["collect", "parse", "view_pdf"]
    }
  ]
}
```

### 6.2 收藏论文

```http
POST /api/papers/{arxiv_id}/collect
```

请求：

```json
{
  "paper": {
    "arxiv_id": "2604.09537v1",
    "title": "Paper Title",
    "pdf_url": "https://arxiv.org/pdf/2604.09537v1"
  }
}
```

响应：

```json
{
  "trace_id": "trace_collect_001",
  "status": "success",
  "message": "论文已收藏"
}
```

### 6.3 解析论文

```http
POST /api/papers/{arxiv_id}/parse
```

响应：

```json
{
  "trace_id": "trace_parse_001",
  "status": "running",
  "message": "论文解析任务已开始"
}
```

### 6.4 查询本地论文

```http
GET /api/library/papers
```

支持 query 参数：

```text
keyword
tag
status
source
page
page_size
```

### 6.5 获取论文详情

```http
GET /api/library/papers/{arxiv_id}
```

### 6.6 删除论文

```http
DELETE /api/library/papers/{arxiv_id}?mode=soft
```

### 6.7 获取解析报告

```http
GET /api/library/papers/{arxiv_id}/report
```

### 6.8 删除解析报告

```http
DELETE /api/library/papers/{arxiv_id}/report
```

### 6.9 重新生成解析报告

```http
POST /api/library/papers/{arxiv_id}/report/regenerate
```

### 6.10 订阅任务 API

```http
GET    /api/subscriptions
POST   /api/subscriptions
GET    /api/subscriptions/{id}
PUT    /api/subscriptions/{id}
DELETE /api/subscriptions/{id}
POST   /api/subscriptions/{id}/run-now
POST   /api/subscriptions/{id}/pause
POST   /api/subscriptions/{id}/resume
```

### 6.11 Trace API

```http
GET /api/traces
GET /api/traces/{trace_id}
```

支持 query 参数：

```text
keyword
tag
task_type
status
date_from
date_to
```

---

## 7. 数据库设计

### 7.1 papers 表

```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    categories TEXT,
    published_date TEXT,
    updated_date TEXT,
    arxiv_url TEXT,
    pdf_url TEXT,
    source TEXT,
    status TEXT DEFAULT 'collected',
    has_pdf INTEGER DEFAULT 0,
    has_parsed_doc INTEGER DEFAULT 0,
    has_report INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

### 7.2 paper_files 表

```sql
CREATE TABLE paper_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    pdf_path TEXT,
    metadata_path TEXT,
    parsed_path TEXT,
    report_path TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### 7.3 paper_summaries 表

```sql
CREATE TABLE paper_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    short_summary TEXT,
    core_problem TEXT,
    method_summary TEXT,
    result_summary TEXT,
    limitation_summary TEXT,
    summary_source TEXT,
    model_name TEXT,
    created_at TEXT
);
```

### 7.4 paper_tags 表

```sql
CREATE TABLE paper_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id TEXT NOT NULL,
    tag TEXT NOT NULL
);
```

### 7.5 subscriptions 表

```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    topics TEXT NOT NULL,
    categories TEXT,
    candidate_k INTEGER DEFAULT 20,
    top_n INTEGER DEFAULT 2,
    cron_expr TEXT NOT NULL,
    timezone TEXT,
    email_enabled INTEGER DEFAULT 0,
    email_to TEXT,
    feishu_enabled INTEGER DEFAULT 0,
    feishu_webhook_ref TEXT,
    auto_parse_full_text INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);
```

### 7.6 subscription_runs 表

```sql
CREATE TABLE subscription_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    run_date TEXT,
    selected_papers TEXT,
    sent_email INTEGER DEFAULT 0,
    sent_feishu INTEGER DEFAULT 0,
    status TEXT,
    error_message TEXT,
    trace_id TEXT,
    created_at TEXT
);
```

### 7.7 tasks 表

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT UNIQUE NOT NULL,
    task_type TEXT NOT NULL,
    user_input TEXT,
    summary TEXT,
    tags TEXT,
    status TEXT,
    started_at TEXT,
    ended_at TEXT,
    duration_ms INTEGER,
    error_message TEXT
);
```

### 7.8 task_steps 表

```sql
CREATE TABLE task_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    tool_name TEXT,
    input_summary TEXT,
    output_summary TEXT,
    status TEXT,
    started_at TEXT,
    ended_at TEXT,
    duration_ms INTEGER,
    error_message TEXT
);
```

### 7.9 user_preferences 表

```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT
);
```

---

## 8. 本地文件系统设计

### 8.1 文件根目录

```text
backend/data/paper_library/
```

### 8.2 单篇论文目录

```text
backend/data/paper_library/papers/{arxiv_id}/
  paper.pdf
  metadata.json
  parsed.md
  report.md
```

### 8.3 metadata.json 示例

```json
{
  "arxiv_id": "2604.09537v1",
  "title": "Paper Title",
  "authors": ["Author A", "Author B"],
  "abstract": "Abstract text",
  "categories": ["cs.CL"],
  "published_date": "2026-04-10",
  "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
  "pdf_url": "https://arxiv.org/pdf/2604.09537v1",
  "source": "manual_search"
}
```

---

## 9. Agent Orchestrator 设计

### 9.1 职责

Agent Orchestrator 负责：

```text
1. 接收用户输入
2. 调用意图识别
3. 调用 query normalization
4. 根据 intent 分发任务
5. 调用对应 tool
6. 记录 trace
7. 返回前端结构化结果
```

### 9.2 伪代码

```python
async def handle_chat(message: str, session_id: str):
    trace = trace_tool.create(task_type="chat", user_input=message)

    intent_result = intent_classifier.classify(message)
    trace.log_step("intent_recognition", output_summary=intent_result)

    normalized = query_normalizer.normalize(intent_result)
    trace.log_step("query_normalization", output_summary=normalized)

    if normalized.intent == "paper_search":
        return await paper_search_flow(normalized, trace)

    if normalized.intent == "subscription_create":
        return await subscription_create_flow(normalized, trace)

    if normalized.intent == "library_search":
        return await library_search_flow(normalized, trace)

    return await general_chat_flow(normalized, trace)
```

---

## 10. 论文检索和重排架构

### 10.1 检索流程

```text
用户 query
→ query normalization
→ query rewrite
→ arXiv API 初筛 candidate_k 篇
→ 构建候选文本 title + abstract + introduction
→ embedding 相似度计算
→ keyword score
→ recency score
→ user preference score
→ final_score
→ Top N
→ LLM 生成卡片摘要
```

### 10.2 评分公式

```text
final_score =
0.45 * semantic_similarity
+ 0.25 * keyword_match_score
+ 0.15 * recency_score
+ 0.15 * user_preference_score
```

### 10.3 搜索阶段内容边界

搜索阶段不解析全文。

只允许：

```text
title
abstract
introduction，可选
```

对应 summary_source：

```text
metadata_only
abstract_intro
```

---

## 11. 订阅任务架构

### 11.1 MVP 定时方式

MVP 使用 APScheduler。

```text
FastAPI 启动时加载 subscriptions 表中 enabled = true 的任务
每个任务注册为 cron job
任务到点后调用 subscription.run
```

### 11.2 正式版

正式版可升级为：

```text
Celery Beat
Redis
Worker
```

### 11.3 订阅运行流程

```text
1. 创建 trace
2. 读取订阅配置
3. 检索 arXiv 候选论文
4. 语义重排
5. 生成每日精选
6. 自动收藏论文
7. 邮件推送
8. 飞书推送
9. 写入 subscription_runs
10. 更新 trace
```

---

## 12. 可观测性架构

### 12.1 Trace 设计

每个完整流程都有一个 trace_id。

常见 trace 类型：

```text
chat
paper_search
paper_collect
paper_parse
library_delete
report_view
subscription_create
subscription_run
email_send
feishu_send
```

### 12.2 Step 设计

每个 trace 由多个 step 组成。

step 示例：

```text
intent_recognition
query_normalization
arxiv_search
candidate_rerank
card_summary_generation
pdf_download
pdf_parse
deep_report_generation
library_write
email_send
feishu_send
```

### 12.3 日志原则

只记录：

```text
输入摘要
输出摘要
状态
耗时
错误信息
```

不记录：

```text
API Key
飞书 webhook 明文
邮箱密码
完整 Prompt
完整 PDF 原文
```

---

## 13. Memory 架构

### 13.1 Memory 类型

```text
UserPreferenceMemory
PaperBehaviorMemory
LocalLibraryMemory
SubscriptionMemory
TraceMemory
```

### 13.2 UserPreferenceMemory

存储在 user_preferences 表。

默认值：

```json
{
  "default_candidate_k": 20,
  "default_top_n": 2,
  "preferred_topics": ["RAG", "Agent", "LLM"],
  "preferred_categories": ["cs.CL", "cs.AI", "cs.LG"],
  "summary_language": "zh-CN",
  "summary_style": "technical",
  "auto_parse_full_text": false
}
```

### 13.3 Memory 使用原则

不要把所有 Memory 都放进 prompt。

只放当前任务必要信息：

```text
当前 query
用户偏好
候选论文 title / abstract / introduction
本次任务上下文
```

---

## 14. Tool 层设计

### 14.1 Tool 清单

```text
intent.classify
query.normalize
arxiv.search
paper.rerank
paper.generate_card_summary
paper.download_pdf
pdf.extract_abstract_intro
pdf.parse_full_text
paper.generate_deep_report
library.add_paper
library.search_papers
library.get_paper
library.delete_paper
library.get_report
library.delete_report
library.regenerate_report
subscription.create
subscription.update
subscription.delete
subscription.run
notify.send_email
notify.send_feishu
trace.create
trace.log_step
trace.query
```

### 14.2 Tool 设计原则

每个 Tool 必须：

```text
输入结构化
输出结构化
失败时返回明确错误
执行前后记录 trace step
不能直接操作前端状态
```

---

## 15. 异步任务设计

### 15.1 必须异步的任务

```text
PDF 全文解析
中文精读报告生成
每日订阅运行
邮件推送
飞书推送
```

### 15.2 前端进度展示

解析任务返回：

```json
{
  "trace_id": "trace_parse_001",
  "status": "running"
}
```

前端通过：

```text
GET /api/traces/{trace_id}
```

轮询任务状态。

后续可升级 WebSocket。

---

## 16. 错误处理规则

### 16.1 arXiv 检索失败

返回：

```text
arXiv 检索失败，请稍后重试。
```

并记录 trace。

### 16.2 PDF 下载失败

记录失败 URL、HTTP 状态、错误原因。

### 16.3 PDF 解析失败

不删除已下载 PDF。

更新论文状态为：

```text
failed
```

### 16.4 邮件 / 飞书推送失败

不影响论文入库。

订阅运行状态可为：

```text
partial_success
```

---

## 17. 环境变量

后端使用 `.env`。

```env
APP_ENV=development
DATABASE_URL=sqlite:///./data/library.db
PAPER_LIBRARY_DIR=./data/paper_library

LLM_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

FEISHU_DEFAULT_WEBHOOK=
```

---

## 18. 开发优先级

### Phase 1

```text
聊天页
意图识别
arXiv 检索
候选论文重排
论文卡片展示
trace 基础记录
```

### Phase 2

```text
收藏论文
PDF 下载
本地论文库页面
论文删除
```

### Phase 3

```text
全文解析
中文精读报告
解析文档查看
解析文档删除 / 重新生成
```

### Phase 4

```text
订阅任务创建
订阅任务 CRUD
每日定时运行
邮箱 / 飞书推送
```

### Phase 5

```text
可观测性详情页
任务搜索
错误定位
用户偏好 Memory
```

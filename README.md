# arXiv Research Agent

> 基于 Streamlit、FastAPI、LangGraph 与 SQLAlchemy 的 arXiv 论文智能检索与自动订阅系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-green.svg)](https://github.com/langchain-ai/langgraph)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-SQLite-orange.svg)](https://www.sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目简介

`arXiv Research Agent` 是一个面向论文检索、研究跟踪与自动推送场景的智能研究助手。

项目围绕“**发现新论文 -> 筛选高相关候选 -> 生成结构化摘要 -> 沉淀为长期订阅 -> 每日自动推送**”这一完整链路设计，支持：

- 使用 `Streamlit` 进行实时论文检索与订阅管理
- 使用 `LangGraph + LLM Tool Calling` 完成 arXiv 检索与论文摘要生成
- 使用 `FastAPI` 提供可调用的后端接口
- 使用 `SQLAlchemy + SQLite` 管理订阅、关键词、接收人和执行记录
- 使用 `APScheduler` 扫描并执行每天到期的订阅任务
- 使用 `SMTP` 或 `飞书 Webhook` 进行每日精选论文推送

相比纯关键词搜索，本项目加入了 **Agent 检索流程、结构化摘要、订阅持久化、跨天去重和多接收人推送**，更接近一个可长期使用的研究情报系统。

---

## 核心能力

### 1. 实时论文检索

- 输入完整 arXiv 查询语句，直接检索最新论文
- 若不提供完整 query，也可以只输入多个关键词
- 系统会自动构造 arXiv 查询语句并执行检索
- 返回论文标题、摘要、作者、发布日期、PDF 链接等信息

### 2. Agent 工作流筛选与总结

- 使用 `LangGraph` 编排检索流程
- 通过 `Tool Calling` 调用 arXiv 搜索工具
- 由 LLM 从候选论文中挑选更相关的论文
- 对保留论文输出结构化字段：
  - 一句话总结
  - 核心问题
  - 方法
  - 结果

### 3. SQLite 订阅系统

- 每条订阅都存入 SQLite，而不是写死在全局配置里
- 每条订阅独立维护：
  - 名称
  - `query` 或 `keywords`
  - `focus`
  - `top_k`
  - `max_results`
  - 执行时间
  - 时区
  - 去重天数
  - 多个接收人

### 4. 自动推送

- 支持多邮箱接收人
- 支持多个飞书群 Webhook
- 每次执行后记录投递结果
- 失败不会阻塞其他接收人继续发送

### 5. 去重与稳定性

- 单次执行内按 `paper.id` 去重
- 跨天根据历史推送记录去重
- 同一订阅同一日期不会重复执行 scheduled run
- 使用线程池并发处理多个到期订阅
- 使用锁避免调度器重复扫描

---

## 系统架构

```text
Streamlit UI (app-run.py)
    ├─ 实时检索 Research Lab
    └─ 订阅管理 Subscription Console
             │
             ▼
FastAPI (app/api/main.py)
    ├─ 搜索接口
    ├─ 订阅 CRUD 接口
    ├─ 手动执行接口
    └─ 执行历史接口
             │
             ▼
DailyDigestService
    ├─ 读取订阅
    ├─ 构造有效 query
    ├─ 调用 LangGraph 工作流
    ├─ 去重筛选论文
    ├─ 生成日报
    └─ 分发到邮箱 / 飞书
             │
             ▼
SQLite (SQLAlchemy)
    ├─ subscriptions
    ├─ subscription_keywords
    ├─ subscription_recipients
    ├─ digest_runs
    ├─ digest_run_items
    └─ digest_deliveries
             │
             ▼
APScheduler
    └─ 每隔 N 分钟扫描所有启用订阅，执行到期任务
```

---

## 运行流程

### 实时检索流程

1. 用户在 Streamlit 中输入 `query` 或 `keywords`
2. `DailyDigestService.generate_digest()` 构造有效查询
3. `ArxivResearchWorkflow` 调用 `search_arxiv`
4. Agent 从候选论文中挑选保留论文
5. `summarize_papers` 输出结构化摘要
6. 前端展示研究报告、工具调用轨迹与论文详情

### 订阅执行流程

1. `APScheduler` 周期性扫描所有启用订阅
2. 判断当前时间是否匹配订阅的 `schedule_hour` 和 `schedule_minute`
3. 创建本次执行记录 `digest_runs`
4. 读取订阅的 `query / keywords / focus / recipients`
5. 运行 LangGraph 工作流生成候选论文
6. 对结果进行：
   - 单次内部去重
   - 跨天去重
7. 生成每日精选报告
8. 按接收人逐个发送通知
9. 记录论文条目与投递结果

---

## 项目结构

```text
arXiv Research Agent/
├─ app-run.py                    # Streamlit 启动入口
├─ app/
│  ├─ config.py                  # 全局配置与环境变量
│  ├─ api/
│  │  ├─ main.py                 # FastAPI 入口与路由
│  │  ├─ contracts.py            # 请求/响应模型
│  │  └─ __init__.py
│  ├─ clients/
│  │  ├─ arxiv_client.py         # arXiv API 客户端
│  │  └─ __init__.py
│  ├─ db/
│  │  ├─ database.py             # SQLAlchemy engine / session / init_db
│  │  ├─ models.py               # SQLite 表结构
│  │  └─ __init__.py
│  ├─ models/
│  │  ├─ paper_models.py         # Pydantic 数据模型
│  │  └─ __init__.py
│  ├─ services/
│  │  ├─ digest_service.py       # 订阅执行、去重、调度核心逻辑
│  │  ├─ notification_service.py # 邮件 / 飞书通知服务
│  │  ├─ subscription_service.py # 订阅 CRUD 与 query 构造
│  │  └─ __init__.py
│  ├─ ui/
│  │  ├─ streamlit_agent_app.py  # Streamlit 前端界面
│  │  └─ __init__.py
│  └─ workflows/
│     ├─ research_agent.py       # LangGraph Agent 工作流
│     └─ __init__.py
├─ data/
│  ├─ arxiv_agent.db             # SQLite 数据库文件
│  └─ chroma/                    # 向量库文件（若存在）
├─ requirements.txt
├─ pyproject.toml
├─ LICENSE
└─ README.md
```

---

## 技术栈

`Python` `Streamlit` `FastAPI` `LangGraph` `LangChain OpenAI Compatible API` `Qwen / DashScope` `SQLAlchemy` `SQLite` `APScheduler` `SMTP` `Feishu Webhook`

---

## 环境要求

- Python 3.10+
- 可访问 arXiv API 的网络环境
- DashScope / Qwen 兼容 API Key
- 如果需要邮件通知，还需要可用的 SMTP 账号

---

## 安装与启动

### 1. 克隆项目

```bash
git clone <your-github-repo-url>
cd arXiv-Research-Agent
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 创建 `.env`

在项目根目录创建 `.env` 文件，示例：

```env
APP_NAME=arXiv Research Agent
ENVIRONMENT=development
TIMEZONE=Asia/Shanghai
LOG_LEVEL=INFO

DASHSCOPE_API_KEY=your_dashscope_api_key
LLM_MODEL=qwen-plus

DATABASE_URL=sqlite:///./data/arxiv_agent.db
REQUEST_TIMEOUT_SECONDS=20

DIGEST_ENABLED=true
SCHEDULER_SCAN_INTERVAL_MINUTES=1
SCHEDULER_MAX_WORKERS=4

SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your_email_account
SMTP_PASSWORD=your_email_password_or_auth_code
SMTP_USE_TLS=true
EMAIL_FROM=your_email_account
```

说明：

- `DASHSCOPE_API_KEY` 用于论文检索后的结构化总结
- 邮件推送只需要在全局配置 SMTP 账号
- 具体收件人、飞书 Webhook、关键词、研究方向都存储在 SQLite 订阅表中

### 4. 启动 Streamlit 前端

```bash
streamlit run app-run.py
```

### 5. 启动 FastAPI 后端

```bash
uvicorn app.api.main:app --reload
```

启动后默认地址：

- Streamlit: `http://localhost:8501`
- FastAPI: `http://127.0.0.1:8000`
- Swagger 文档: `http://127.0.0.1:8000/docs`

---

## 前端界面说明

Streamlit 前端包含两个主要工作区：

### 1. Research Lab

用于即时检索与探索研究方向：

- 输入 `arXiv Query`
- 或只输入关键词列表
- 输入研究关注点 `Focus`
- 设置 `Top K` 与 `Max Results`
- 查看：
  - 研究摘要报告
  - Tool Trace
  - 论文详情

### 2. Subscription Console

用于订阅管理：

- 创建新订阅
- 编辑已有订阅
- 删除订阅
- 手动试跑
- 查看最近执行记录
<img width="1340" height="817" alt="屏幕截图 2026-04-15 113257" src="https://github.com/user-attachments/assets/6690fd84-d58e-4b5c-aad2-f91aeb99ff06" />

---

## FastAPI 接口

### 健康检查

```http
GET /health
```

返回调度器状态、扫描间隔和时区。

### 实时搜索

```http
POST /api/v1/research/search
```

示例请求：

```json
{
  "query": "cat:cs.AI OR cat:cs.CL",
  "keywords": [],
  "focus": "LLM Agent, RAG, reasoning",
  "top_k": 5,
  "max_results": 50,
  "api_key": "your_dashscope_api_key"
}
```

### 订阅管理

```http
GET    /api/v1/subscriptions
POST   /api/v1/subscriptions
GET    /api/v1/subscriptions/{id}
PUT    /api/v1/subscriptions/{id}
DELETE /api/v1/subscriptions/{id}
```

### 执行记录

```http
GET /api/v1/subscriptions/{id}/runs
```

### 手动执行订阅

```http
POST /api/v1/subscriptions/{id}/run
```

示例请求：

```json
{
  "notify": true,
  "api_key": "your_dashscope_api_key"
}
```

---

## SQLite 数据表设计

### `subscriptions`

存储订阅主配置：

- 订阅名称
- query
- focus
- top_k
- max_results
- schedule_hour / schedule_minute
- timezone
- dedupe_days
- enabled

### `subscription_keywords`

存储订阅的关键词列表。

当 `query` 为空时，系统自动将这些关键词构造成有效 arXiv 查询：

```text
all:"keyword1" OR all:"keyword2" OR all:"keyword3"
```

### `subscription_recipients`

存储接收人：

- `channel = email`
- `channel = feishu`

### `digest_runs`

记录每次订阅执行情况：

- 手动触发 / 定时触发
- 状态
- 论文数
- 错误信息
- 开始 / 结束时间

### `digest_run_items`

记录本次推送涉及到的论文，用于跨天去重。

### `digest_deliveries`

记录每个接收人的投递结果。

---

## 去重与调度策略

### 单次去重

同一次执行中，对论文按 `paper.id` 去重，避免重复论文进入最终精选列表。

### 跨天去重

根据 `digest_run_items` 中的历史记录，在 `dedupe_days` 范围内跳过已经推送过的论文。

### 调度方式

项目不是为每条订阅单独注册一个 cron 任务，而是：

1. 由 APScheduler 每隔 `SCHEDULER_SCAN_INTERVAL_MINUTES` 扫描一次
2. 找到“当前分钟应执行”的订阅
3. 用线程池并发执行

这种方式更适合订阅配置经常变更的场景。

### 并发与幂等

- 使用 `_schedule_lock` 避免重复扫描
- `digest_runs` 中 `(subscription_id, scheduled_for_date)` 唯一约束，防止同一天重复 scheduled run
- 某个订阅失败不会影响其他订阅继续执行

---

## 通知机制

### 邮件推送

邮件账号通过 `.env` 全局配置：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

具体收件人地址不在 `.env` 中配置，而是写入订阅表。

### 飞书推送

每个飞书群的 `Webhook URL` 作为接收人保存在订阅表中，可实现：

- 一个订阅推送到多个飞书群
- 不同订阅推送到不同群

---

## 适合写进简历 / 面试的亮点

- 从单文件原型重构为 `Streamlit + FastAPI + LangGraph + SQLAlchemy` 的模块化系统
- 支持 **实时检索 + 持久化订阅 + 自动推送** 的完整闭环
- 使用 `SQLite` 设计订阅、执行、投递等完整数据模型
- 引入 **多关键词自动构造 query、跨天去重、并发执行与错误隔离**
- 同时提供前端交互界面和后端 API，具备较好的产品化与工程化展示价值

---

## 已知说明

- 项目默认依赖 DashScope 兼容接口进行结构化摘要生成
- 若没有可用的 `DASHSCOPE_API_KEY`，搜索工作流无法完整执行摘要步骤
- 邮件发送依赖可用 SMTP 账号
- 飞书通知依赖有效的群机器人 Webhook

---

## 后续可扩展方向

- 增加用户系统与登录鉴权
- 增加订阅标签、分组与搜索
- 增加推送模板与 Markdown / 卡片消息
- 接入更多论文源，如 Semantic Scholar、OpenReview
- 增加论文全文解析与向量检索
- 增加 Docker 部署与 CI/CD

---

## License

本项目采用 [MIT License](LICENSE)。

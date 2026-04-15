# arXiv Research Agent

一个面向论文检索与自动订阅场景的 arXiv 智能助手，支持：

- Streamlit 交互式检索
- LangGraph Agent 工作流
- FastAPI 服务化接口
- SQLite 订阅管理
- 多关键词自动构造 arXiv 查询
- 多接收人邮件 / 飞书推送
- 每日定时扫描订阅并发送精选论文
- 单次内部去重与跨天去重

## 项目结构

```text
arXiv Research Agent/
├─ app/
│  ├─ api/          # FastAPI 接口
│  ├─ clients/      # arXiv 等外部客户端
│  ├─ db/           # SQLAlchemy 数据层
│  ├─ models/       # Pydantic 数据模型
│  ├─ services/     # 订阅、通知、日报服务
│  ├─ ui/           # Streamlit 页面
│  └─ workflows/    # LangGraph 工作流
├─ data/            # SQLite 数据文件
├─ .env.example
├─ demo1.py
└─ requirements.txt
```

## 快速开始

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.api.main:app --reload
```

另开一个终端启动前端：

```powershell
streamlit run demo1.py
```

## 订阅能力

订阅配置全部存储在 SQLite 中，不再依赖单条全局 query / focus / webhook 配置。

每条订阅可配置：

- 订阅名称
- `query` 或 `keywords`
- 研究关注点 `focus`
- `top_k` / `max_results`
- 定时发送时间
- 时区
- 跨天去重天数
- 多个接收人（邮箱或飞书）

当 `query` 为空时，系统会自动将 `keywords` 拼装成 arXiv 查询语句。

## 关键接口

- `GET /health`
- `POST /api/v1/research/search`
- `GET /api/v1/subscriptions`
- `POST /api/v1/subscriptions`
- `GET /api/v1/subscriptions/{id}`
- `PUT /api/v1/subscriptions/{id}`
- `DELETE /api/v1/subscriptions/{id}`
- `GET /api/v1/subscriptions/{id}/runs`
- `POST /api/v1/subscriptions/{id}/run`

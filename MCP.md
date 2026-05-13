# MCP.md

# arXiv 论文助手 Agent MCP 接口设计文档

## 1. 文档目的

本文档用于指导 Claude 或其他 AI 编程助手实现本项目的 MCP Server。

本项目的主应用是：

```text
Vue3 前端 + FastAPI 后端 + 本地文献库 + 定时订阅任务
```

MCP 不是第一阶段必须完成的功能，但它是后续扩展 Agent 能力的重要接口层。

MCP 的作用是把项目能力标准化暴露出去，让不同客户端或大模型可以通过统一协议调用本项目能力，例如：

```text
搜索 arXiv 论文
下载 PDF
解析论文
读取本地论文库
查看解析报告
创建每日订阅
查询任务流程
```

---

## 2. MCP 在本项目中的定位

### 2.1 MCP 不是前端 API 的替代品

前端 Vue3 页面仍然调用 FastAPI HTTP API。

MCP Server 主要用于：

```text
1. 给 AI Agent / Claude / Cursor / ChatGPT 等工具调用
2. 把本地论文库暴露为可读取资源
3. 把论文搜索、解析、订阅等流程暴露为工具
4. 把常用提示词流程暴露为 Prompt
```

### 2.2 推荐架构

```text
Vue3 前端
  ↓
FastAPI HTTP API
  ↓
业务服务层
  ↓
数据库 / 文件系统 / 外部服务

MCP Client
  ↓
MCP Server
  ↓
同一套业务服务层
  ↓
数据库 / 文件系统 / 外部服务
```

也就是说：

```text
HTTP API 和 MCP Server 复用同一套 service / tool 逻辑
不要为 MCP 单独复制一套业务代码
```

---

## 3. MCP Server 名称

推荐名称：

```text
arxiv-paper-agent-mcp
```

服务能力：

```text
arXiv paper search
paper collect
paper parse
local library management
daily subscription management
trace query
```

---

## 4. MCP 能力分层

MCP Server 暴露三类内容：

```text
Tools     动作型能力，可被模型调用
Resources 数据型能力，可被模型读取
Prompts   可复用提示词模板
```

设计原则：

```text
动作做成 Tool
数据做成 Resource
流程提示词做成 Prompt
```

---

## 5. MCP Tools 总览

### 5.1 Tool 分类

```text
1. arXiv 检索类 Tools
2. 论文筛选和摘要类 Tools
3. PDF 下载和解析类 Tools
4. 本地论文库类 Tools
5. 订阅任务类 Tools
6. 推送通知类 Tools
7. 可观测性类 Tools
```

---

## 6. arXiv 检索类 Tools

## 6.1 arxiv.search_papers

### 功能

根据用户输入的研究方向搜索 arXiv 论文。

用于：

```text
给我找 2 篇关于 agent 的论文
推荐最近关于 RAG evaluation 的论文
找一些 LLM Agent 方向的新论文
```

### 输入参数

```json
{
  "query": "string",
  "max_results": 20,
  "categories": ["cs.CL", "cs.AI", "cs.LG"],
  "sort_by": "relevance",
  "date_from": "string | null",
  "date_to": "string | null"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| query | string | 是 | 用户研究方向或关键词 |
| max_results | number | 否 | 候选池大小，默认 20 |
| categories | string[] | 否 | arXiv 分类 |
| sort_by | string | 否 | relevance / submittedDate / lastUpdatedDate |
| date_from | string | 否 | 起始日期 |
| date_to | string | 否 | 结束日期 |

### 返回结果

```json
{
  "success": true,
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "authors": ["Author A", "Author B"],
      "abstract": "Abstract text",
      "categories": ["cs.CL"],
      "published_date": "2026-04-10",
      "updated_date": "2026-04-12",
      "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
      "pdf_url": "https://arxiv.org/pdf/2604.09537v1"
    }
  ],
  "error": null
}
```

### 约束

```text
1. 不下载 PDF
2. 不做全文解析
3. 只返回元数据
4. 如果 arXiv 失败，需要返回明确错误
```

---

## 6.2 arxiv.get_paper_metadata

### 功能

根据 arXiv ID 获取单篇论文元数据。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1"
}
```

### 返回结果

```json
{
  "success": true,
  "paper": {
    "arxiv_id": "2604.09537v1",
    "title": "Paper Title",
    "authors": ["Author A"],
    "abstract": "Abstract text",
    "categories": ["cs.CL"],
    "published_date": "2026-04-10",
    "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
    "pdf_url": "https://arxiv.org/pdf/2604.09537v1"
  }
}
```

---

## 7. 论文筛选和摘要类 Tools

## 7.1 paper.rerank_candidates

### 功能

从 arXiv 候选池中筛选最相关的 Top N 论文。

用于：

```text
先召回 candidate_k 篇论文
再根据语义匹配和用户偏好筛选 top_n 篇
```

### 输入参数

```json
{
  "query": "agent",
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "abstract": "Abstract text",
      "categories": ["cs.CL"],
      "published_date": "2026-04-10"
    }
  ],
  "top_n": 2,
  "user_preferences": {
    "preferred_topics": ["RAG", "Agent", "LLM"],
    "preferred_categories": ["cs.CL", "cs.AI", "cs.LG"],
    "blocked_keywords": []
  }
}
```

### 推荐评分公式

```text
final_score =
0.45 * semantic_similarity
+ 0.25 * keyword_match_score
+ 0.15 * recency_score
+ 0.15 * user_preference_score
```

### 返回结果

```json
{
  "success": true,
  "ranked_papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "final_score": 0.91,
      "semantic_similarity": 0.89,
      "keyword_match_score": 0.95,
      "recency_score": 0.82,
      "user_preference_score": 0.96,
      "reason": "与用户查询 agent 高度相关，并匹配用户偏好的 LLM Agent 方向"
    }
  ]
}
```

---

## 7.2 paper.generate_card_summary

### 功能

为搜索结果页生成论文卡片摘要。

### 重要边界

此 Tool 只能基于：

```text
title
abstract
introduction，可选
```

不能使用完整 PDF 正文。

不能声称已经阅读全文。

### 输入参数

```json
{
  "paper": {
    "arxiv_id": "2604.09537v1",
    "title": "Paper Title",
    "abstract": "Abstract text",
    "introduction": "Introduction text, optional"
  },
  "query": "agent",
  "language": "zh-CN"
}
```

### 返回结果

```json
{
  "success": true,
  "summary": {
    "summary": "本文提出...",
    "core_problem": "现有方法存在...",
    "method": "作者提出...",
    "result": "摘要和引言显示...",
    "recommendation_reason": "适合关注 Agent 方向的用户快速阅读",
    "summary_source": "abstract_intro"
  }
}
```

### summary_source 可选值

```text
metadata_only
abstract_intro
full_text
```

本 Tool 只允许返回：

```text
metadata_only
abstract_intro
```

---

## 8. PDF 下载和解析类 Tools

## 8.1 paper.download_pdf

### 功能

根据 arXiv ID 和 PDF URL 下载 PDF 到本地文献库。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1",
  "pdf_url": "https://arxiv.org/pdf/2604.09537v1",
  "source": "manual_search"
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "pdf_path": "backend/data/paper_library/papers/2604.09537v1/paper.pdf",
  "already_exists": false
}
```

### 约束

```text
1. 下载前检查文件是否已存在
2. 已存在则不重复下载
3. 下载失败必须返回错误
4. 不生成 parsed.md
5. 不生成 report.md
```

---

## 8.2 pdf.extract_abstract_intro

### 功能

轻量提取 PDF 中的 Abstract 和 Introduction。

用于搜索结果卡片增强。

### 输入参数

```json
{
  "pdf_path": "backend/data/paper_library/papers/2604.09537v1/paper.pdf"
}
```

### 返回结果

```json
{
  "success": true,
  "abstract": "Abstract text",
  "introduction": "Introduction text",
  "parsed_source": "pdf_light"
}
```

### 约束

```text
1. 这是轻量解析
2. 不生成完整 parsed.md
3. 不生成 report.md
4. 失败时可以退回 metadata_only 摘要
```

---

## 8.3 pdf.parse_full_text

### 功能

解析完整 PDF，生成结构化全文 Markdown。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1",
  "pdf_path": "backend/data/paper_library/papers/2604.09537v1/paper.pdf"
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "parsed_path": "backend/data/paper_library/papers/2604.09537v1/parsed.md",
  "sections": [
    {
      "title": "Abstract",
      "content": "..."
    },
    {
      "title": "Introduction",
      "content": "..."
    },
    {
      "title": "Method",
      "content": "..."
    }
  ]
}
```

### 约束

```text
1. 只在用户点击“解析”或订阅开启 auto_parse_full_text 时调用
2. 解析失败不删除 PDF
3. 需要记录 trace step
```

---

## 8.4 paper.generate_deep_report

### 功能

根据完整 parsed.md 生成中文精读报告 report.md。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1",
  "parsed_markdown": "full parsed paper content",
  "metadata": {
    "title": "Paper Title",
    "authors": ["Author A"],
    "published_date": "2026-04-10"
  },
  "user_research_direction": "RAG, Agent, LLM"
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "report_path": "backend/data/paper_library/papers/2604.09537v1/report.md",
  "summary_source": "full_text"
}
```

### 报告结构

```markdown
# 论文中文精读报告

## 1. 论文基本信息
## 2. 一句话总结
## 3. 研究背景
## 4. 核心问题
## 5. 方法详解
## 6. 关键创新点
## 7. 实验设计
## 8. 主要结果
## 9. 局限性
## 10. 对用户研究方向的价值
## 11. 可复现性判断
```

---

## 9. 本地论文库类 Tools

## 9.1 library.add_paper

### 功能

把论文加入本地文献库。

收藏和解析都会调用此 Tool。

### 输入参数

```json
{
  "paper": {
    "arxiv_id": "2604.09537v1",
    "title": "Paper Title",
    "authors": ["Author A"],
    "abstract": "Abstract text",
    "categories": ["cs.CL"],
    "published_date": "2026-04-10",
    "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
    "pdf_url": "https://arxiv.org/pdf/2604.09537v1"
  },
  "files": {
    "pdf_path": "backend/data/paper_library/papers/2604.09537v1/paper.pdf",
    "metadata_path": "backend/data/paper_library/papers/2604.09537v1/metadata.json",
    "parsed_path": null,
    "report_path": null
  },
  "source": "manual_search",
  "status": "collected",
  "tags": ["agent"]
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "status": "collected"
}
```

---

## 9.2 library.search_papers

### 功能

搜索本地论文库。

### 输入参数

```json
{
  "keyword": "agent",
  "tags": ["agent"],
  "status": "collected",
  "source": "manual_search",
  "page": 1,
  "page_size": 20
}
```

### 返回结果

```json
{
  "success": true,
  "total": 1,
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "authors": ["Author A"],
      "status": "collected",
      "has_pdf": true,
      "has_parsed_doc": false,
      "has_report": false,
      "source": "manual_search",
      "created_at": "2026-05-12 08:00:00"
    }
  ]
}
```

---

## 9.3 library.get_paper

### 功能

读取本地库中某篇论文详情。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1"
}
```

### 返回结果

```json
{
  "success": true,
  "paper": {
    "arxiv_id": "2604.09537v1",
    "title": "Paper Title",
    "metadata": {},
    "files": {
      "pdf_path": "...",
      "metadata_path": "...",
      "parsed_path": "...",
      "report_path": "..."
    }
  }
}
```

---

## 9.4 library.delete_paper

### 功能

删除本地论文。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1",
  "delete_mode": "soft"
}
```

### delete_mode

```text
soft：软删除，只更新 status = deleted
hard：硬删除，删除数据库记录和本地文件
```

MVP 默认只使用 soft。

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "delete_mode": "soft",
  "status": "deleted"
}
```

---

## 9.5 library.get_report

### 功能

读取某篇论文的中文解析报告。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1"
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "report_markdown": "# 论文中文精读报告\n..."
}
```

---

## 9.6 library.delete_report

### 功能

删除某篇论文的解析报告。

### 输入参数

```json
{
  "arxiv_id": "2604.09537v1"
}
```

### 返回结果

```json
{
  "success": true,
  "arxiv_id": "2604.09537v1",
  "has_report": false,
  "has_parsed_doc": false
}
```

### 约束

```text
删除解析报告不删除 PDF
删除 report.md 可同时删除 parsed.md
```

---

## 10. 订阅任务类 Tools

## 10.1 subscription.create

### 功能

创建每日论文订阅任务。

### 输入参数

```json
{
  "name": "RAG-Agent-LLM 每日精选",
  "topics": ["RAG", "Agent", "LLM"],
  "categories": ["cs.CL", "cs.AI", "cs.LG"],
  "candidate_k": 20,
  "top_n": 2,
  "schedule": {
    "type": "daily",
    "time": "08:00",
    "timezone": "Asia/Shanghai"
  },
  "channels": {
    "email": {
      "enabled": true,
      "to": ["xxx@example.com"]
    },
    "feishu": {
      "enabled": true,
      "webhook_ref": "feishu_group_001"
    }
  },
  "auto_parse_full_text": false
}
```

### 返回结果

```json
{
  "success": true,
  "subscription_id": 1,
  "enabled": true
}
```

---

## 10.2 subscription.list

### 功能

列出订阅任务。

### 输入参数

```json
{
  "enabled": true
}
```

### 返回结果

```json
{
  "success": true,
  "subscriptions": [
    {
      "id": 1,
      "name": "RAG-Agent-LLM 每日精选",
      "topics": ["RAG", "Agent", "LLM"],
      "top_n": 2,
      "candidate_k": 20,
      "schedule": "0 8 * * *",
      "enabled": true
    }
  ]
}
```

---

## 10.3 subscription.update

### 功能

修改订阅任务。

### 输入参数

```json
{
  "subscription_id": 1,
  "patch": {
    "topics": ["RAG", "Agent"],
    "top_n": 3,
    "enabled": true
  }
}
```

---

## 10.4 subscription.delete

### 功能

删除订阅任务。

### 输入参数

```json
{
  "subscription_id": 1
}
```

---

## 10.5 subscription.run_now

### 功能

立即运行一次订阅任务。

### 输入参数

```json
{
  "subscription_id": 1
}
```

### 返回结果

```json
{
  "success": true,
  "trace_id": "trace_subscription_run_001",
  "status": "running"
}
```

---

## 10.6 subscription.run_digest

### 功能

执行完整每日精选流程。

此 Tool 可由定时任务调用，也可由 `subscription.run_now` 调用。

### 输入参数

```json
{
  "subscription_id": 1,
  "dry_run": false
}
```

### 内部流程

```text
1. 读取订阅配置
2. 检索 arXiv 候选论文
3. 语义重排 Top N
4. 生成每日精选摘要
5. 自动收藏论文到本地库
6. 邮件推送
7. 飞书推送
8. 写入 subscription_runs
9. 写入 trace
```

---

## 11. 推送通知类 Tools

## 11.1 notify.send_email

### 功能

发送每日精选到邮箱。

### 输入参数

```json
{
  "to": ["xxx@example.com"],
  "subject": "今日 arXiv 精选",
  "content_markdown": "# 今日 arXiv 精选\n...",
  "attachments": []
}
```

### 返回结果

```json
{
  "success": true,
  "sent": true
}
```

---

## 11.2 notify.send_feishu

### 功能

发送每日精选到飞书群。

### 输入参数

```json
{
  "webhook_ref": "feishu_group_001",
  "title": "今日 arXiv 精选",
  "content_markdown": "# 今日 arXiv 精选\n..."
}
```

### 返回结果

```json
{
  "success": true,
  "sent": true
}
```

### 安全要求

```text
1. MCP 参数中不要出现飞书 webhook 明文
2. 使用 webhook_ref 从后端安全配置中读取
3. trace 中不要记录 webhook 明文
```

---

## 12. 可观测性类 Tools

## 12.1 trace.query

### 功能

查询任务流程记录。

### 输入参数

```json
{
  "keyword": "agent",
  "task_type": "paper_search",
  "status": "success",
  "tag": "topic:agent",
  "date_from": "2026-05-01",
  "date_to": "2026-05-12",
  "page": 1,
  "page_size": 20
}
```

### 返回结果

```json
{
  "success": true,
  "total": 1,
  "traces": [
    {
      "trace_id": "trace_20260512_0001",
      "task_type": "paper_search",
      "summary": "搜索 2 篇关于 agent 的论文",
      "tags": ["paper_search", "topic:agent"],
      "status": "success",
      "started_at": "2026-05-12 08:00:00",
      "duration_ms": 4000
    }
  ]
}
```

---

## 12.2 trace.get

### 功能

获取某个 trace 的完整步骤。

### 输入参数

```json
{
  "trace_id": "trace_20260512_0001"
}
```

### 返回结果

```json
{
  "success": true,
  "trace": {
    "trace_id": "trace_20260512_0001",
    "task_type": "paper_search",
    "summary": "搜索 2 篇关于 agent 的论文",
    "status": "success",
    "steps": [
      {
        "step_name": "intent_recognition",
        "status": "success",
        "duration_ms": 120,
        "input_summary": "用户输入论文搜索请求",
        "output_summary": "intent=paper_search"
      }
    ]
  }
}
```

---

## 13. MCP Resources 设计

Resources 用来暴露本地论文库和任务数据。

### 13.1 本地论文库 Resources

```text
library://papers/all
library://papers/recent
library://papers/collected
library://papers/parsed
library://papers/deleted
library://papers/source/manual_search
library://papers/source/daily_digest
library://papers/tag/{tag}
```

### 13.2 单篇论文 Resources

```text
library://paper/{arxiv_id}/metadata
library://paper/{arxiv_id}/pdf
library://paper/{arxiv_id}/parsed
library://paper/{arxiv_id}/report
library://paper/{arxiv_id}/summary
```

示例：

```text
library://paper/2604.09537v1/report
```

返回：

```json
{
  "arxiv_id": "2604.09537v1",
  "content_type": "text/markdown",
  "content": "# 论文中文精读报告\n..."
}
```

### 13.3 订阅任务 Resources

```text
subscription://all
subscription://enabled
subscription://disabled
subscription://{subscription_id}
subscription://{subscription_id}/runs
```

### 13.4 Trace Resources

```text
trace://recent
trace://failed
trace://{trace_id}
trace://tag/{tag}
```

---

## 14. MCP Prompts 设计

Prompts 用于向模型提供标准任务模板。

### 14.1 prompt://paper/card_summary_zh

用途：

```text
基于 title + abstract + introduction 生成中文论文卡片
```

输入：

```json
{
  "title": "string",
  "abstract": "string",
  "introduction": "string | null",
  "query": "string"
}
```

输出字段：

```text
总结
核心问题
方法
结果
推荐理由
summary_source
```

约束：

```text
不得编造全文内容
不得声称已阅读全文
不确定时明确说明
```

---

### 14.2 prompt://paper/deep_report_zh

用途：

```text
基于完整 PDF 解析内容生成中文精读报告
```

输入：

```json
{
  "metadata": {},
  "parsed_markdown": "string",
  "user_research_direction": "string"
}
```

输出：

```markdown
# 论文中文精读报告

## 1. 论文基本信息
## 2. 一句话总结
## 3. 研究背景
## 4. 核心问题
## 5. 方法详解
## 6. 关键创新点
## 7. 实验设计
## 8. 主要结果
## 9. 局限性
## 10. 对用户研究方向的价值
## 11. 可复现性判断
```

---

### 14.3 prompt://digest/daily_arxiv_zh

用途：

```text
生成每日 arXiv 精选推送内容
```

输入：

```json
{
  "date": "2026-05-12",
  "topics": ["RAG", "Agent", "LLM"],
  "papers": []
}
```

输出：

```markdown
# 今日 arXiv 精选

日期：
关注方向：

## 今日推荐

### 1. 论文标题
- arXiv：
- PDF：
- 一句话总结：
- 核心问题：
- 方法：
- 结果：
- 推荐理由：
- 阅读建议：

## 今日趋势观察

## 已自动入库论文
```

---

### 14.4 prompt://library/paper_card_zh

用途：

```text
把本地论文库中的论文整理为中文卡片
```

输入：

```json
{
  "paper": {},
  "report": "optional markdown"
}
```

输出：

```text
标题
状态
标签
一句话总结
是否已解析
可执行操作建议
```

---

## 15. MCP Server 目录结构建议

```text
mcp_server/
  server.py
  tools/
    arxiv_tools.py
    paper_tools.py
    pdf_tools.py
    library_tools.py
    subscription_tools.py
    notify_tools.py
    trace_tools.py

  resources/
    library_resources.py
    subscription_resources.py
    trace_resources.py

  prompts/
    paper_prompts.py
    digest_prompts.py
    library_prompts.py

  schemas/
    tools.py
    resources.py
    prompts.py

  README.md
```

原则：

```text
MCP tools 只做协议适配
具体业务逻辑调用 backend/app/services 和 backend/app/tools
不要在 mcp_server 中重复实现业务逻辑
```

---

## 16. MCP 与 FastAPI 共享代码规则

MCP Tool 应该调用已有 service：

```text
MCP Tool
→ service
→ tool
→ db / storage / external API
```

不要这样：

```text
MCP Tool
→ 直接操作数据库
→ 直接写文件
→ 直接请求 arXiv
```

除非该能力还没有 service，此时应先抽象 service。

---

## 17. MCP 安全规则

### 17.1 不暴露敏感信息

MCP 返回中禁止包含：

```text
LLM API Key
邮箱密码
SMTP 密码
飞书 webhook 明文
数据库连接字符串
完整系统 Prompt
```

### 17.2 删除操作限制

对于 MCP 删除操作：

```text
默认 soft delete
hard delete 需要显式 delete_mode = hard
hard delete 必须由上层客户端二次确认
```

### 17.3 文件路径暴露

MCP 可以返回本地逻辑路径，但不建议返回系统绝对路径。

推荐：

```text
paper_library/papers/2604.09537v1/paper.pdf
```

不推荐：

```text
/Users/name/project/backend/data/paper_library/...
```

---

## 18. MCP 错误返回格式

所有 Tool 统一返回：

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "message": "用户可理解的错误信息",
  "detail": "开发者可查看的简短错误摘要",
  "trace_id": "trace_xxx"
}
```

常见错误码：

```text
ARXIV_SEARCH_FAILED
PAPER_NOT_FOUND
PDF_DOWNLOAD_FAILED
PDF_PARSE_FAILED
REPORT_GENERATION_FAILED
LIBRARY_WRITE_FAILED
SUBSCRIPTION_NOT_FOUND
EMAIL_SEND_FAILED
FEISHU_SEND_FAILED
TRACE_NOT_FOUND
```

---

## 19. MCP 开发优先级

### Phase 1

```text
arxiv.search_papers
paper.rerank_candidates
paper.generate_card_summary
library.search_papers
library.get_paper
trace.query
trace.get
```

### Phase 2

```text
paper.download_pdf
library.add_paper
library.delete_paper
library.get_report
```

### Phase 3

```text
pdf.parse_full_text
paper.generate_deep_report
library.delete_report
```

### Phase 4

```text
subscription.create
subscription.list
subscription.update
subscription.delete
subscription.run_now
```

### Phase 5

```text
notify.send_email
notify.send_feishu
Resources
Prompts
```

---

## 20. MCP 验收标准

MCP 完成后，应满足：

```text
1. 可通过 MCP 搜索 arXiv 论文
2. 可通过 MCP 筛选 Top N 论文
3. 可通过 MCP 读取本地论文库
4. 可通过 MCP 读取某篇论文报告
5. 可通过 MCP 创建订阅任务
6. 可通过 MCP 查询 trace
7. MCP 调用不会泄露敏感配置
8. MCP 和 FastAPI 复用同一套业务逻辑
```

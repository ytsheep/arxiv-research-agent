# PRD.md

# arXiv 论文助手 Agent 产品需求文档

## 1. 项目概述

本项目是一个以聊天界面为主要入口的 arXiv 论文助手 Agent。

用户可以通过自然语言完成论文检索、论文收藏、PDF 下载、论文解析、本地文献库管理、每日论文订阅推送和任务流程查询。

项目目标不是做一个简单的论文搜索器，而是做一个完整的科研论文工作流系统：

```text
聊天触发任务
→ arXiv 论文检索
→ 候选论文筛选
→ 论文卡片展示
→ 用户收藏或解析
→ 本地文献库沉淀
→ 每日订阅自动推送
→ 全流程可观测和可追踪
```

---

## 2. 产品定位

### 2.1 产品名称

暂定名称：

```text
Arxiv Paper Agent
```

也可以后续改为：

```text
PaperPilot
Research Agent
Daily Arxiv Assistant
```

### 2.2 目标用户

主要面向：

- AI / NLP / LLM / Agent / RAG 方向学习者
- 科研人员
- 工程开发者
- 需要每日追踪论文的人
- 需要本地文献管理和论文解析的人

### 2.3 核心价值

用户不需要手动打开 arXiv 搜索、筛选、下载、保存、整理和总结论文。

系统提供：

1. 自然语言论文检索
2. 论文候选池筛选
3. 中文论文卡片摘要
4. 一键收藏 PDF
5. 一键全文解析并生成中文精读报告
6. 本地论文库管理
7. 每日自动精选论文并推送邮箱 / 飞书
8. 每次任务全流程可查询

---

## 3. 功能范围

### 3.1 核心功能列表

| 编号 | 功能模块 | 说明 |
|---|---|---|
| F1 | 聊天式论文检索 | 用户通过聊天输入研究方向，系统检索 arXiv 并返回 Top N 论文 |
| F2 | 论文收藏 | 用户点击收藏后，系统下载 PDF 并保存到本地库 |
| F3 | 论文解析 | 用户点击解析后，系统全文解析 PDF 并生成中文精读报告 |
| F4 | 本地论文库 CRUD | 查看、搜索、删除本地论文 |
| F5 | 解析文档 CRUD | 查看、删除、重新生成解析文档 |
| F6 | 每日订阅任务 | 用户通过聊天或页面创建定时论文推送任务 |
| F7 | 邮箱 / 飞书推送 | 每日精选论文发送到指定邮箱和飞书群 |
| F8 | 订阅任务 CRUD | 查看、创建、修改、暂停、删除订阅任务 |
| F9 | 可观测性流程查询 | 每次交互生成 trace，可查看完整执行链路和错误位置 |
| F10 | 用户偏好 Memory | 记录候选池大小、默认返回数量、关注主题、推送偏好等 |

---

## 4. 前端页面设计

前端采用 Vue 3。

### 4.1 页面模块

前端包含四个主要模块：

```text
1. 聊天交互页
2. 本地论文库页
3. 订阅任务管理页
4. 任务流程查询页
```

---

## 5. 模块 1：聊天交互页

### 5.1 功能描述

聊天页是系统主要入口。

用户可以输入：

```text
给我找 2 篇关于 agent 的论文
给我推荐 3 篇最近关于 RAG evaluation 的论文
把第一篇收藏
解析第二篇论文
给我每天早上 8 点发送 2 篇关于 RAG、Agent、LLM 的论文到邮箱和飞书群
```

系统需要识别用户意图并执行对应任务。

---

### 5.2 意图识别

系统采用：

```text
小模型意图识别 + 关键词规则兜底
```

小模型需要输出结构化 JSON。

示例：

```json
{
  "intent": "paper_search",
  "confidence": 0.94,
  "entities": {
    "topic": "agent",
    "top_n": 2,
    "candidate_k": 20,
    "need_parse": false,
    "need_collect": false,
    "language": "zh-CN"
  }
}
```

---

### 5.3 支持的意图类型

| intent | 说明 |
|---|---|
| paper_search | 搜索论文 |
| paper_collect | 收藏论文 |
| paper_parse | 解析论文 |
| library_search | 查询本地论文 |
| library_delete | 删除本地论文 |
| report_view | 查看解析文档 |
| report_delete | 删除解析文档 |
| report_regenerate | 重新生成解析文档 |
| subscription_create | 创建订阅任务 |
| subscription_update | 修改订阅任务 |
| subscription_delete | 删除订阅任务 |
| subscription_list | 查看订阅任务 |
| trace_search | 查询任务流程 |
| general_chat | 普通闲聊 |
| unsupported | 不支持的问题 |

---

### 5.4 关键词兜底规则

当小模型置信度较低时，使用关键词兜底。

规则示例：

```text
包含 “找 / 搜 / 推荐 / 论文 / paper / arxiv” → paper_search
包含 “收藏 / 保存 / 加入本地库” → paper_collect
包含 “解析 / 精读 / 总结全文 / 深度阅读” → paper_parse
包含 “每天 / 每周 / 定时 / 早上 / 发送 / 推送” → subscription_create
包含 “删除 / 移除” + “论文” → library_delete
包含 “删除 / 移除” + “解析文档 / 报告” → report_delete
包含 “流程 / 记录 / 报错 / 日志 / 任务” → trace_search
```

---

### 5.5 输入纠错和 Query Normalization

需要处理用户输入中的拼写错误。

示例：

```text
agnet → agent
llm → LLM
rag → RAG
agentic → agent
```

Query Normalization 后再调用 arXiv 检索。

---

### 5.6 论文搜索流程

用户输入：

```text
给我找 2 篇关于 agnet 的论文
```

系统执行：

```text
1. 识别意图：paper_search
2. 提取 topic = agnet，top_n = 2
3. query normalization：agnet → agent
4. 读取系统设置 candidate_k，例如 k = 20
5. 从 arXiv 检索 20 篇候选论文
6. 使用语义匹配 / rerank 从 20 篇中筛选 Top 2
7. 只基于 title + abstract + introduction 生成论文卡片
8. 前端展示 Top 2 论文
9. 记录 trace
```

---

### 5.7 候选池和 Top N

系统设置里需要支持：

```text
candidate_k：每次从 arXiv 初筛召回多少篇论文，默认 20
top_n：最终返回给用户多少篇论文，默认根据用户输入；如果用户未指定，默认 2
```

示例：

```text
用户：给我找 2 篇关于 agent 的论文
candidate_k = 20
top_n = 2
```

含义：

```text
先检索 20 篇关于 agent 的论文
再从 20 篇中筛选最相关的 2 篇展示
```

---

### 5.8 搜索阶段摘要边界

搜索结果页不能做全文解析。

搜索阶段只允许基于：

```text
title
abstract
introduction，可选
```

生成如下内容：

```text
总结
核心问题
方法
结果
```

搜索阶段的 summary_source 应标记为：

```text
abstract_intro
```

如果没有提取 introduction，则标记为：

```text
metadata_only
```

禁止在搜索阶段声称“阅读全文后发现”。

---

### 5.9 论文卡片展示格式

论文卡片需要展示：

```text
标题
arXiv 链接
PDF 链接
作者
发布时间
分类
总结
核心问题
方法
结果
summary_source
操作按钮
```

示例：

```text
Case-Grounded Evidence Verification: A Framework for Constructing Evidence-Sensitive Supervision

arXiv: http://arxiv.org/abs/2604.09537v1
PDF: https://arxiv.org/pdf/2604.09537v1

总结：
本文提出一种无需人工标注的证据验证监督构造方法，使 LLM 能真正依据证据做因果判断，解决了 RAG 中“证据摆设化”的核心瓶颈。

核心问题：
现有证据增强推理中监督信号薄弱，证据与主张关联松散，模型难以真正依赖证据做决策。

方法：
提出案例驱动的证据验证框架，通过自动生成语义可控的正例和负例，构建强监督信号。

结果：
实验显示验证器优于多个基线，并在证据移除或替换时性能下降，说明模型确实依赖证据。

按钮：
[收藏] [解析] [查看 PDF] [不感兴趣]
```

---

## 6. 模块 1 子功能：收藏论文

### 6.1 功能描述

用户点击论文卡片上的“收藏”按钮后，系统将论文 PDF 下载到本地文献库，并保存论文元数据。

### 6.2 收藏流程

```text
1. 用户点击收藏
2. 创建 collect_paper trace
3. 检查本地是否已有该论文
4. 如果没有，下载 PDF
5. 保存 metadata.json
6. 写入 papers 表
7. 标记 has_pdf = true
8. 标记 has_report = false
9. 返回收藏成功
```

### 6.3 收藏后文件结构

```text
paper_library/
  papers/
    2604.09537v1/
      paper.pdf
      metadata.json
```

### 6.4 收藏验收标准

- 点击收藏后，论文出现在本地文献库
- 本地可以找到 PDF 文件
- 数据库中 has_pdf = true
- 不应自动生成 parsed.md 和 report.md
- 重复收藏同一篇论文时不应重复下载，应该提示已收藏

---

## 7. 模块 1 子功能：解析论文

### 7.1 功能描述

用户点击论文卡片上的“解析”按钮后，系统下载 PDF，解析全文，并生成中文精读报告。

### 7.2 解析流程

```text
1. 用户点击解析
2. 创建 parse_paper trace
3. 检查 PDF 是否存在
4. 如果不存在，先下载 PDF
5. 调用 PDF 全文解析
6. 生成 parsed.md
7. 将解析结果输入大模型
8. 生成中文精读报告 report.md
9. 保存到本地文献库
10. 更新数据库状态
11. 前端显示解析完成
```

### 7.3 解析后文件结构

```text
paper_library/
  papers/
    2604.09537v1/
      paper.pdf
      metadata.json
      parsed.md
      report.md
```

### 7.4 中文精读报告结构

```markdown
# 论文中文精读报告

## 1. 论文基本信息
- 标题：
- 作者：
- arXiv ID：
- 发布时间：
- 研究方向：

## 2. 一句话总结

## 3. 研究背景

## 4. 核心问题

## 5. 方法详解

## 6. 关键创新点

## 7. 实验设计
- 数据集：
- Baseline：
- 评价指标：
- 实验设置：

## 8. 主要结果

## 9. 局限性

## 10. 对用户研究方向的价值

## 11. 可复现性判断
- 是否有代码：
- 是否有数据：
- 是否有超参数：
- 复现难度：高 / 中 / 低
```

### 7.5 解析验收标准

- 点击解析后，论文 PDF 必须保存到本地
- 必须生成 parsed.md
- 必须生成 report.md
- 本地文献库状态更新为 parsed
- 前端可以查看 report.md
- 如果解析失败，可观测性模块能看到失败步骤

---

## 8. 模块 2：本地论文库 CRUD 和解析文档查看

### 8.1 页面名称

```text
本地文献库
```

### 8.2 功能范围

本地文献库支持：

```text
1. 查看已收藏论文
2. 搜索论文
3. 按标签筛选论文
4. 按状态筛选论文
5. 查看 PDF 链接
6. 查看解析文档
7. 删除论文
8. 删除解析文档
9. 重新生成解析文档
```

### 8.3 论文状态

| 状态 | 含义 |
|---|---|
| collected | 仅收藏 PDF 和元数据 |
| parsed | 已全文解析并生成报告 |
| deleted | 已软删除 |
| failed | 收藏或解析失败 |

### 8.4 本地论文表格字段

```text
标题
arXiv ID
作者
发布时间
分类
标签
状态
来源
收藏时间
操作
```

操作按钮：

```text
[查看详情] [查看 PDF] [解析] [查看解析文档] [删除]
```

### 8.5 解析文档查看

点击“查看解析文档”后：

- 在当前页面右侧抽屉或新页面中显示 Markdown 渲染结果
- 支持复制 Markdown
- 支持下载 Markdown
- 支持删除解析文档
- 支持重新生成解析文档

### 8.6 删除论文

删除模式分为：

```text
soft：软删除，只更新数据库状态，不删除文件
hard：硬删除，删除数据库记录和本地文件
```

MVP 默认使用 soft。

### 8.7 验收标准

- 本地文献库能列出所有已收藏论文
- 可以根据关键词搜索
- 可以删除论文
- 可以打开解析报告
- 可以删除解析报告
- 删除解析报告不应删除 PDF
- 删除论文后，默认不在普通列表中显示

---

## 9. 模块 3：每日订阅推送

### 9.1 功能描述

用户可以通过聊天创建每日论文推送任务。

示例：

```text
给我每天早上 8 点钟都发送 2 篇关于 RAG，Agent，LLM 的论文到 xxx 邮箱，xxx 飞书群
```

系统识别后创建订阅任务。

### 9.2 订阅任务解析结果

```json
{
  "intent": "subscription_create",
  "entities": {
    "topics": ["RAG", "Agent", "LLM"],
    "top_n": 2,
    "candidate_k": 20,
    "schedule": {
      "type": "daily",
      "time": "08:00",
      "timezone": "Asia/Shanghai"
    },
    "channels": {
      "email": {
        "enabled": true,
        "to": "xxx@example.com"
      },
      "feishu": {
        "enabled": true,
        "target": "某某某飞书群"
      }
    }
  }
}
```

### 9.3 每日订阅运行流程

```text
1. 到达设定时间
2. 创建 subscription_run trace
3. 根据 topics 检索 arXiv 候选论文
4. 使用 candidate_k 获取候选池
5. 使用语义匹配和用户偏好筛选 Top N
6. 生成每日中文精选
7. 自动收藏论文到本地库
8. 发送邮箱
9. 发送飞书
10. 记录运行结果
```

### 9.4 每日精选是否全文解析

默认不做全文解析。

默认只基于：

```text
title
abstract
introduction，可选
```

生成每日精选。

订阅任务可以配置：

```text
auto_parse_full_text = false
```

如果用户开启全文解析，才对每日精选论文生成完整解析报告。

### 9.5 每日精选报告格式

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
- 阅读建议：精读 / 略读 / 收藏

### 2. 论文标题
...

## 今日趋势观察

## 已自动入库论文
```

### 9.6 推送渠道

MVP 支持：

```text
邮箱
飞书群机器人 webhook
```

### 9.7 验收标准

- 用户能通过聊天创建订阅任务
- 订阅任务出现在订阅任务管理页
- 到点后自动执行
- 推送内容发送到邮箱
- 推送内容发送到飞书
- 被推送论文自动加入本地库
- 每次订阅运行都生成 trace
- 推送失败能在流程查询中看到错误

---

## 10. 模块 4：订阅任务 CRUD

### 10.1 页面名称

```text
订阅任务
```

### 10.2 功能范围

支持：

```text
1. 查看订阅任务
2. 创建订阅任务
3. 修改订阅任务
4. 暂停订阅任务
5. 启用订阅任务
6. 删除订阅任务
7. 立即运行订阅任务
8. 查看最近运行结果
```

### 10.3 表格字段

```text
任务名称
关注主题
每日推送数量
候选池大小
推送时间
推送渠道
是否自动全文解析
状态
最近运行时间
最近运行结果
操作
```

操作按钮：

```text
[查看] [编辑] [暂停/启用] [立即运行] [删除]
```

### 10.4 验收标准

- 可以创建订阅任务
- 可以修改关注主题
- 可以修改推送时间
- 可以修改推送数量
- 可以启用 / 暂停
- 可以删除
- 可以立即运行
- 可以查看最近运行记录

---

## 11. 模块 5：可观测性流程查询

### 11.1 功能描述

每一次用户交互、收藏、解析、订阅运行、推送都必须产生 trace。

trace 用于：

```text
1. 查询任务历史
2. 复盘执行过程
3. 定位失败步骤
4. 查看工具调用摘要
5. 查看耗时和错误原因
```

### 11.2 Trace 示例

```json
{
  "trace_id": "trace_20260512_0001",
  "task_type": "paper_search",
  "summary": "搜索 2 篇关于 agent 的论文",
  "tags": ["paper_search", "topic:agent", "top_n:2", "candidate_k:20"],
  "status": "success",
  "started_at": "2026-05-12 08:00:00",
  "ended_at": "2026-05-12 08:00:04",
  "duration_ms": 4000
}
```

### 11.3 任务步骤示例

```text
intent_recognition       success
query_normalization      success
arxiv_search             success
candidate_rerank         success
card_summary_generation  success
frontend_render          success
```

失败示例：

```text
candidate_rerank         failed

错误原因：
Embedding 服务超时
```

### 11.4 前端查询能力

支持：

```text
按关键词搜索
按标签搜索
按任务类型筛选
按状态筛选
按时间筛选
```

### 11.5 日志安全要求

禁止在日志中保存：

```text
邮箱密码
飞书 webhook 明文
完整 API Key
完整 Prompt
完整 PDF 正文
用户隐私信息
```

只保存摘要和脱敏信息。

### 11.6 验收标准

- 每次聊天交互都有 trace
- 每次收藏都有 trace
- 每次解析都有 trace
- 每次订阅运行都有 trace
- 失败任务能看到失败步骤
- 支持按标签搜索任务
- 支持查看完整任务时间线

---

## 12. Memory 设计需求

系统需要五类 Memory。

### 12.1 用户偏好 Memory

记录：

```json
{
  "default_candidate_k": 20,
  "default_top_n": 2,
  "preferred_topics": ["RAG", "Agent", "LLM"],
  "preferred_categories": ["cs.CL", "cs.AI", "cs.LG"],
  "summary_language": "zh-CN",
  "summary_style": "技术精读",
  "auto_parse_full_text": false,
  "blocked_keywords": []
}
```

### 12.2 论文行为 Memory

记录：

```text
收藏过哪些论文
解析过哪些论文
删除过哪些论文
不感兴趣的论文
经常搜索的主题
```

用于后续推荐排序。

### 12.3 本地文献 Memory

本地文献库本身就是长期 Memory，包括：

```text
PDF
metadata
parsed.md
report.md
tags
status
source
```

### 12.4 订阅任务 Memory

记录：

```text
用户有哪些订阅
订阅主题
推送时间
推送渠道
最近推送过哪些论文
```

用于防重复推荐。

### 12.5 可观测性 Memory

记录任务流程，不直接喂给大模型，只用于查询和调试。

---

## 13. 非功能需求

### 13.1 性能

- 普通聊天响应应在 3 秒内返回
- 论文检索结果应在 15 秒内返回
- 收藏任务应在 30 秒内完成
- 全文解析任务可以异步执行
- 前端需要显示解析进度

### 13.2 稳定性

- arXiv API 失败时，需要提示用户稍后重试
- PDF 下载失败时，需要记录失败原因
- 解析失败时，不应破坏已收藏论文数据
- 推送失败时，应保留订阅运行记录

### 13.3 可扩展性

后续应容易增加：

```text
Zotero 同步
Obsidian 导出
Notion 同步
本地向量库问答
多论文对比
Related Work 自动写作
```

### 13.4 安全性

- API Key 使用环境变量
- 飞书 webhook 加密或脱敏存储
- 日志不记录敏感凭据
- 删除操作需要前端二次确认
- 硬删除需要额外确认

---

## 14. 明确不做的功能

MVP 不做：

```text
1. 多论文自动综述
2. Related Work 自动写作
3. Zotero 同步
4. Notion 同步
5. Obsidian 双向同步
6. 全库问答 RAG
7. 多用户权限系统
8. 复杂团队协作
```

这些可以作为后续版本。

---

## 15. MVP 验收标准

MVP 完成标准：

```text
1. 用户可以在聊天页输入“给我找 2 篇关于 agent 的论文”
2. 系统能返回 2 张论文卡片
3. 论文卡片包含标题、链接、总结、核心问题、方法、结果
4. 用户可以点击收藏
5. 收藏后 PDF 和 metadata 保存到本地
6. 用户可以点击解析
7. 解析后生成 report.md
8. 本地文献库页面能查看论文
9. 本地文献库页面能查看解析报告
10. 用户可以创建每日订阅任务
11. 订阅任务可以定时执行并发送邮箱 / 飞书
12. 每次任务都能在流程查询页看到 trace
13. 失败任务可以看到失败步骤和错误原因
```

---

## 16. Agent Capability Expansion Requirements

### 16.1 Goal

Upgrade the assistant from a paper-search agent into a research-workflow agent.
The agent should help users search, read, compare, summarize, remember preferences,
and diagnose failures. Subscription creation and notification sending must remain
manual page features and must not be exposed as autonomous Agent Skill/Tool flows.

### 16.2 In Scope

The Agent should support the following natural-language tasks:

```text
1. Search papers by topic and return paper cards.
2. Recommend papers based on the user's long-term interests.
3. Resolve follow-up references such as "the second paper" or "that previous paper".
4. Deep-read a selected paper and generate a full reading report.
5. Compare multiple papers by problem, method, experiment, result, limitation, and value.
6. Produce a small literature survey for a research topic.
7. Update and query user research preferences.
8. Diagnose failed Agent or workflow traces.
```

### 16.3 Out of Scope For Agent Autonomy

Do not add Agent Skill/Tool capabilities for:

```text
1. Creating subscription tasks.
2. Updating subscription schedules.
3. Sending email.
4. Sending Feishu/Lark notifications.
5. Any external send operation without a manual UI action.
```

Subscription and notification features should remain in the existing manual UI pages.

### 16.4 Required Skills

Implement or register these high-level Skills:

```text
paper_search_card_skill
paper_deep_read_skill
paper_compare_skill
literature_survey_skill
interest_recommendation_skill
memory_profile_skill
trace_diagnosis_skill
```

The ReAct subgraph should prefer Skills over raw Tools. Raw Tools are available for
Skill internals and narrow low-risk operations.

### 16.5 Required Tools

Expose these Agent-callable Tools through Tool Registry:

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
library_get_paper
library_get_report
paper_collect
paper_parse_full_text
paper_generate_deep_report
semantic_memory_search
user_preference_get
user_preference_update
trace_query
trace_get
```

Do not register subscription or notification Tools for ReAct use.

### 16.6 Intent And Query Rewrite Requirements

Intent routing must use a three-layer design:

```text
1. Rule-based high-confidence routing for explicit tasks.
2. LLM structured intent classification with fixed JSON schema.
3. Backend validation with Pydantic schemas, Tool Registry, and business guards.
```

The router must produce:

```json
{
  "intent": "paper_deep_read",
  "selected_skill": "paper_deep_read_skill",
  "confidence": 0.91,
  "slots": {
    "topic": "",
    "paper_ref": "second_last_result",
    "top_n": 2
  },
  "needs_clarification": false,
  "rewritten_query": "",
  "reason": "User asked to deep-read the second paper from previous results."
}
```

Query rewrite is required for:

```text
1. Paper search: convert natural Chinese/English request into research keywords.
2. Interest recommendation: generate query from user preferences and semantic memory.
3. Follow-up search: generate query from the referenced previous paper.
4. Literature survey: expand topic into broader academic search terms.
```

Always keep both original query and rewritten query in State and Trace summaries.

### 16.7 Acceptance Criteria

The implementation is complete only when these user tasks work:

```text
1. "Find 2 papers about agent memory."
2. "Find papers similar to the second one."
3. "Deep-read the second paper and generate a report."
4. "Compare these two papers."
5. "Make a small literature survey about RAG agents."
6. "Find two papers I am interested in."
7. "In the future, recommend more RAG Agent papers and fewer CV papers."
8. "Why did the last task fail?"
```

Every task must return a trace_id and must be visible in the Trace page.

# SKILLS.md

# arXiv 论文助手 Agent Skills 技能设计文档

## 1. 文档目的

本文档用于指导 Claude 编写本项目的 Skill 技能包。

Skill 不是单个函数，也不是普通 Prompt。

在本项目中，Skill 表示：

```text
一套可复用的任务流程
一组明确的输入输出规范
一套稳定的提示词约束
一条固定的工具调用链
一组质量标准和失败处理规则
```

本项目核心 Skill 用于把复杂科研任务沉淀为可复用能力，例如：

```text
论文搜索卡片生成
论文全文解析
每日 arXiv 精选推送
本地论文库管理
任务流程诊断
```

---

## 2. Skill 和 Tool 的区别

### 2.1 Tool

Tool 是一个动作。

示例：

```text
arxiv.search_papers
paper.download_pdf
pdf.parse_full_text
library.add_paper
notify.send_email
```

特点：

```text
输入明确
输出明确
动作单一
通常不包含复杂判断流程
```

### 2.2 Skill

Skill 是一个完整流程。

示例：

```text
paper_search_card_skill
paper_deep_parse_skill
daily_arxiv_digest_skill
```

特点：

```text
包含多个步骤
会调用多个 Tool
有触发条件
有输入输出格式
有质量标准
有失败处理策略
```

---

## 3. 本项目 Skill 总览

核心 Skill：

```text
1. paper_search_card_skill
   论文搜索卡片生成技能

2. paper_deep_parse_skill
   论文全文解析和中文精读报告技能

3. daily_arxiv_digest_skill
   每日 arXiv 精选和推送技能

4. local_library_manage_skill
   本地论文库管理技能

5. trace_diagnosis_skill
   任务流程查询和错误诊断技能
```

MVP 必须优先实现前三个：

```text
paper_search_card_skill
paper_deep_parse_skill
daily_arxiv_digest_skill
```

---

## 4. Skill 目录结构建议

推荐目录：

```text
skills/
  paper_search_card_skill/
    SKILL.md
    examples/
      input_search_agent.json
      output_paper_cards.json
    prompts/
      card_summary_zh.md

  paper_deep_parse_skill/
    SKILL.md
    examples/
      input_parse_paper.json
      output_report.md
    prompts/
      deep_report_zh.md

  daily_arxiv_digest_skill/
    SKILL.md
    examples/
      input_subscription.json
      output_digest.md
    prompts/
      daily_digest_zh.md

  local_library_manage_skill/
    SKILL.md
    examples/
      input_search_library.json
      output_library_results.json

  trace_diagnosis_skill/
    SKILL.md
    examples/
      input_trace_query.json
      output_trace_diagnosis.md
```

每个 Skill 至少包含：

```text
SKILL.md
prompts/
examples/
```

---

# 5. Skill 1：paper_search_card_skill

## 5.1 技能名称

```text
paper_search_card_skill
```

## 5.2 技能目标

根据用户输入的论文搜索需求，从 arXiv 检索候选论文，进行语义重排，并生成中文论文卡片。

该 Skill 用于聊天页搜索结果展示。

---

## 5.3 触发条件

用户输入包含以下意图：

```text
找论文
搜论文
推荐论文
arXiv 论文
paper
关于某方向的论文
```

示例：

```text
给我找 2 篇关于 agent 的论文
推荐 3 篇 RAG evaluation 方向的论文
找最近关于 LLM Agent 的 arXiv 论文
```

---

## 5.4 输入

```json
{
  "user_message": "给我找2篇关于agnet的论文",
  "session_id": "session_001",
  "user_preferences": {
    "default_candidate_k": 20,
    "default_top_n": 2,
    "preferred_topics": ["RAG", "Agent", "LLM"],
    "preferred_categories": ["cs.CL", "cs.AI", "cs.LG"],
    "summary_language": "zh-CN"
  }
}
```

---

## 5.5 输出

```json
{
  "type": "paper_search_result",
  "trace_id": "trace_001",
  "message": "找到 2 篇相关论文",
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "authors": ["Author A", "Author B"],
      "published_date": "2026-04-10",
      "categories": ["cs.CL"],
      "arxiv_url": "http://arxiv.org/abs/2604.09537v1",
      "pdf_url": "https://arxiv.org/pdf/2604.09537v1",
      "summary": "本文提出...",
      "core_problem": "现有方法存在...",
      "method": "作者提出...",
      "result": "摘要和引言显示...",
      "recommendation_reason": "与用户关注的 Agent 方向相关",
      "summary_source": "abstract_intro",
      "actions": ["collect", "parse", "view_pdf"]
    }
  ]
}
```

---

## 5.6 工具调用链

```text
1. intent.classify
2. query.normalize
3. arxiv.search_papers
4. paper.rerank_candidates
5. paper.generate_card_summary
6. trace.log_step
```

可选：

```text
pdf.extract_abstract_intro
```

注意：

```text
搜索阶段默认不下载完整 PDF
除非为了抽取 Introduction 且系统允许临时缓存
```

---

## 5.7 执行流程

```text
1. 创建 trace
2. 识别 intent = paper_search
3. 提取 topic、top_n、candidate_k
4. 对 query 做纠错，例如 agnet → agent
5. 读取用户偏好中的 candidate_k
6. 调用 arxiv.search_papers 召回候选论文
7. 调用 paper.rerank_candidates 做语义重排
8. 选出 Top N
9. 调用 paper.generate_card_summary 生成中文卡片
10. 返回前端
11. 写入 trace 成功状态
```

---

## 5.8 摘要生成 Prompt 模板

文件位置：

```text
skills/paper_search_card_skill/prompts/card_summary_zh.md
```

内容：

```markdown
你是一个科研论文阅读助手。

你只能基于用户提供的论文标题、摘要和引言内容生成总结。
不要使用任何外部知识补充论文内容。
不要声称已经阅读全文。
如果摘要或引言中没有明确提到结果，请写“给定内容中未明确说明”。

用户关注方向：
{{query}}

论文标题：
{{title}}

论文摘要：
{{abstract}}

论文引言：
{{introduction}}

请用中文输出 JSON：

{
  "summary": "一句话总结这篇论文做了什么",
  "core_problem": "论文试图解决的核心问题",
  "method": "论文提出的方法",
  "result": "论文在给定内容中体现的结果或发现",
  "recommendation_reason": "为什么推荐给关注该方向的用户",
  "summary_source": "metadata_only 或 abstract_intro"
}
```

---

## 5.9 质量标准

```text
1. 不得编造论文正文内容
2. 不得夸大论文贡献
3. 不得输出“全文证明”等表述
4. 必须标注 summary_source
5. 用户要求 top_n = 2 时，只返回 2 篇
6. 如果 arXiv 搜索不到，应给出清晰提示
```

---

## 5.10 失败处理

### arXiv 搜索失败

返回：

```text
arXiv 检索失败，请稍后重试。
```

同时 trace 标记为 failed。

### 候选论文不足

返回已有数量，并说明：

```text
只找到 N 篇相关论文。
```

### LLM 摘要失败

可以退回简单模板：

```text
标题：
摘要：
推荐原因：与用户关键词匹配。
```

---

# 6. Skill 2：paper_deep_parse_skill

## 6.1 技能名称

```text
paper_deep_parse_skill
```

## 6.2 技能目标

当用户点击“解析”或明确要求精读论文时，下载 PDF，解析全文，并生成中文精读报告。

---

## 6.3 触发条件

用户点击前端按钮：

```text
解析
```

或用户输入：

```text
解析这篇论文
精读这篇论文
帮我生成这篇论文的中文报告
总结全文
```

---

## 6.4 输入

```json
{
  "arxiv_id": "2604.09537v1",
  "paper": {
    "title": "Paper Title",
    "pdf_url": "https://arxiv.org/pdf/2604.09537v1",
    "authors": ["Author A"],
    "abstract": "Abstract text"
  },
  "user_research_direction": "RAG, Agent, LLM",
  "source": "manual_search"
}
```

---

## 6.5 输出

```json
{
  "type": "paper_parse_result",
  "trace_id": "trace_parse_001",
  "status": "success",
  "arxiv_id": "2604.09537v1",
  "pdf_path": "paper_library/papers/2604.09537v1/paper.pdf",
  "parsed_path": "paper_library/papers/2604.09537v1/parsed.md",
  "report_path": "paper_library/papers/2604.09537v1/report.md",
  "summary_source": "full_text"
}
```

---

## 6.6 工具调用链

```text
1. trace.create
2. library.get_paper，可选
3. paper.download_pdf，如果 PDF 不存在
4. pdf.parse_full_text
5. paper.generate_deep_report
6. library.add_paper 或 library.update_paper
7. trace.log_step
```

---

## 6.7 执行流程

```text
1. 创建 parse_paper trace
2. 检查本地库是否已有 PDF
3. 如果 PDF 不存在，下载 PDF
4. 保存 metadata.json
5. 调用 pdf.parse_full_text 生成 parsed.md
6. 将 parsed.md 和 metadata 输入 LLM
7. 生成 report.md
8. 更新 papers 表：
   status = parsed
   has_pdf = true
   has_parsed_doc = true
   has_report = true
9. 返回解析完成
```

---

## 6.8 中文精读报告 Prompt 模板

文件位置：

```text
skills/paper_deep_parse_skill/prompts/deep_report_zh.md
```

内容：

```markdown
你是一个严谨的科研论文精读助手。

你将基于一篇论文的完整解析文本生成中文精读报告。

要求：
1. 只能基于给定论文内容分析，不要编造论文没有的信息。
2. 如果某些信息没有出现，请写“论文中未明确说明”。
3. 需要区分作者明确提出的结论和你的分析判断。
4. 报告要适合技术学习者阅读。
5. 不要写成营销文案。

用户关注方向：
{{user_research_direction}}

论文元数据：
{{metadata}}

论文完整解析内容：
{{parsed_markdown}}

请按以下结构输出 Markdown：

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

## 12. 建议阅读方式
- 精读章节：
- 可略读章节：
- 适合记录到笔记的内容：
```

---

## 6.9 报告质量标准

```text
1. 必须是 Markdown
2. 必须包含所有一级标题
3. 不确定内容必须明确说明
4. 不能把摘要中的推测当成实验证据
5. 不能过度拔高贡献
6. 必须说明和用户研究方向的关系
7. 必须标注 summary_source = full_text
```

---

## 6.10 失败处理

### PDF 下载失败

```text
保留论文元数据
状态标记 failed
trace 记录 PDF_DOWNLOAD_FAILED
```

### PDF 解析失败

```text
保留 PDF
不生成 report.md
状态标记 failed
trace 记录 PDF_PARSE_FAILED
```

### 报告生成失败

```text
保留 parsed.md
不删除 PDF
状态标记 failed
trace 记录 REPORT_GENERATION_FAILED
```

---

# 7. Skill 3：daily_arxiv_digest_skill

## 7.1 技能名称

```text
daily_arxiv_digest_skill
```

## 7.2 技能目标

根据用户配置的主题，每天定时检索 arXiv，筛选 Top N 论文，生成中文每日精选，推送到邮箱 / 飞书，并自动存入本地论文库。

---

## 7.3 触发条件

用户通过聊天创建订阅：

```text
给我每天早上8点发送2篇关于RAG，Agent，LLM的论文到邮箱和飞书群
```

或系统定时任务触发：

```text
subscription.run
```

---

## 7.4 输入

```json
{
  "subscription_id": 1,
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

---

## 7.5 输出

```json
{
  "type": "daily_digest_result",
  "trace_id": "trace_subscription_run_001",
  "subscription_id": 1,
  "status": "success",
  "selected_papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "summary": "..."
    }
  ],
  "sent_email": true,
  "sent_feishu": true,
  "digest_path": "paper_library/digests/2026-05-12.md"
}
```

---

## 7.6 工具调用链

```text
1. trace.create
2. subscription.get
3. arxiv.search_papers
4. paper.rerank_candidates
5. paper.generate_card_summary
6. digest.generate_daily_digest
7. paper.download_pdf
8. library.add_paper
9. notify.send_email
10. notify.send_feishu
11. subscription.record_run
12. trace.log_step
```

如果 auto_parse_full_text = true，额外调用：

```text
pdf.parse_full_text
paper.generate_deep_report
```

---

## 7.7 执行流程

```text
1. 创建 subscription_run trace
2. 读取订阅配置
3. 根据 topics 组合搜索 query
4. 对每个 topic 或组合 query 检索 arXiv
5. 合并候选论文，去重
6. 根据 candidate_k 截断候选池
7. 根据语义相似度、关键词、时间、用户偏好重排
8. 选出 Top N
9. 生成中文每日精选 Markdown
10. 自动下载 Top N 论文 PDF
11. 写入本地论文库，source = daily_digest
12. 如果 auto_parse_full_text = true，则生成完整 report.md
13. 发送邮箱
14. 发送飞书
15. 写入 subscription_runs
16. 更新 trace 状态
```

---

## 7.8 每日精选 Prompt 模板

文件位置：

```text
skills/daily_arxiv_digest_skill/prompts/daily_digest_zh.md
```

内容：

```markdown
你是一个 arXiv 每日论文精选助手。

你需要根据用户关注方向和候选论文信息，生成中文每日精选报告。

注意：
1. 默认只基于标题、摘要和引言生成总结。
2. 如果没有全文解析，不要写“全文指出”。
3. 每篇论文都要说明为什么值得读。
4. 推荐理由要和用户关注主题相关。
5. 输出适合邮件和飞书群阅读。

日期：
{{date}}

用户关注方向：
{{topics}}

候选论文：
{{papers}}

请输出 Markdown：

# 今日 arXiv 精选

日期：{{date}}
关注方向：{{topics}}

## 今日推荐

### 1. {{paper_title}}
- arXiv：
- PDF：
- 一句话总结：
- 核心问题：
- 方法：
- 结果：
- 推荐理由：
- 阅读建议：精读 / 略读 / 收藏

### 2. {{paper_title}}
...

## 今日趋势观察

## 已自动入库论文
```

---

## 7.9 质量标准

```text
1. 每日推送论文数量必须等于 top_n，除非候选不足
2. 每篇论文必须包含 arXiv 和 PDF 链接
3. 每篇论文必须自动入库
4. 默认不全文解析
5. 发送失败不能影响论文入库
6. 邮箱或飞书失败时，状态可为 partial_success
7. 必须记录 subscription_run
8. 必须记录 trace
```

---

## 7.10 防重复规则

每日推送时应避免重复推荐。

规则：

```text
1. 最近 7 天推送过的论文不再推送
2. 本地库已存在且 source = daily_digest 的论文降低排序
3. 用户标记不感兴趣的论文不再推送
```

---

## 7.11 失败处理

### arXiv 搜索失败

```text
订阅运行失败
不发送空邮件
记录 trace
```

### 邮件失败，飞书成功

```text
status = partial_success
sent_email = false
sent_feishu = true
```

### 飞书失败，邮件成功

```text
status = partial_success
sent_email = true
sent_feishu = false
```

### 论文入库失败

```text
继续尝试推送
但在 digest 中不要声明“已入库”
trace 记录入库失败
```

---

# 8. Skill 4：local_library_manage_skill

## 8.1 技能名称

```text
local_library_manage_skill
```

## 8.2 技能目标

管理本地论文库，包括查询论文、读取论文详情、查看报告、删除论文、删除报告、重新生成报告。

---

## 8.3 触发条件

用户输入：

```text
查看我收藏的论文
本地库里有哪些 Agent 论文
打开这篇论文的解析文档
删除这篇论文
删除这篇论文的解析报告
重新生成报告
```

或前端页面按钮触发：

```text
查看详情
查看报告
删除
重新生成报告
```

---

## 8.4 输入示例

```json
{
  "action": "search",
  "keyword": "agent",
  "filters": {
    "status": "parsed",
    "source": "manual_search",
    "tags": ["agent"]
  }
}
```

---

## 8.5 输出示例

```json
{
  "type": "library_search_result",
  "trace_id": "trace_library_001",
  "papers": [
    {
      "arxiv_id": "2604.09537v1",
      "title": "Paper Title",
      "status": "parsed",
      "has_pdf": true,
      "has_report": true
    }
  ]
}
```

---

## 8.6 工具调用链

按 action 分发：

### search

```text
library.search_papers
trace.log_step
```

### get_paper

```text
library.get_paper
trace.log_step
```

### get_report

```text
library.get_report
trace.log_step
```

### delete_paper

```text
library.delete_paper
trace.log_step
```

### delete_report

```text
library.delete_report
trace.log_step
```

### regenerate_report

```text
library.get_paper
pdf.parse_full_text，可选
paper.generate_deep_report
library.update_paper
trace.log_step
```

---

## 8.7 删除规则

```text
默认 soft delete
删除论文默认不物理删除文件
删除报告不删除 PDF
硬删除必须二次确认
```

---

## 8.8 质量标准

```text
1. 搜索结果必须过滤 deleted 状态，除非用户明确查看已删除
2. 删除操作必须记录 trace
3. 查看报告时如果 report.md 不存在，应提示“该论文尚未生成解析报告”
4. 重新生成报告时，如果 PDF 不存在，应提示先重新下载 PDF
```

---

# 9. Skill 5：trace_diagnosis_skill

## 9.1 技能名称

```text
trace_diagnosis_skill
```

## 9.2 技能目标

帮助用户查询任务记录，查看完整流程，定位失败步骤和错误原因。

---

## 9.3 触发条件

用户输入：

```text
刚才那个任务为什么失败了
查看 agent 搜索任务
查一下今天失败的任务
这篇论文解析在哪里报错了
查看订阅推送记录
```

或前端任务流程页查询。

---

## 9.4 输入

```json
{
  "keyword": "agent",
  "task_type": "paper_search",
  "status": "failed",
  "date_from": "2026-05-12",
  "date_to": "2026-05-12"
}
```

---

## 9.5 输出

```json
{
  "type": "trace_diagnosis_result",
  "traces": [
    {
      "trace_id": "trace_20260512_0001",
      "summary": "搜索 2 篇关于 agent 的论文",
      "status": "failed",
      "failed_step": "candidate_rerank",
      "error_message": "Embedding 服务超时"
    }
  ]
}
```

---

## 9.6 工具调用链

```text
trace.query
trace.get
trace.summarize_failure，可选
```

---

## 9.7 输出格式

如果用户查询单个失败任务，输出：

```markdown
# 任务诊断结果

任务：
状态：
失败步骤：
错误原因：
已完成步骤：
未完成步骤：
建议处理方式：
```

---

## 9.8 安全规则

```text
1. 不显示 API Key
2. 不显示飞书 webhook 明文
3. 不显示邮箱密码
4. 不显示完整 Prompt
5. 不显示完整 PDF 正文
```

---

# 10. Skill 之间的协作关系

```text
paper_search_card_skill
  → 用户找到论文
  → 点击收藏：local_library_manage_skill
  → 点击解析：paper_deep_parse_skill

daily_arxiv_digest_skill
  → 每日自动找论文
  → 自动收藏：local_library_manage_skill
  → 可选解析：paper_deep_parse_skill

trace_diagnosis_skill
  → 查询所有 Skill 执行过程
```

---

# 11. Skill 执行中的 trace 规则

每个 Skill 必须创建 trace。

### paper_search_card_skill

```text
trace.task_type = paper_search
tags = ["paper_search", "topic:{topic}", "top_n:{top_n}"]
```

### paper_deep_parse_skill

```text
trace.task_type = paper_parse
tags = ["paper_parse", "arxiv_id:{arxiv_id}"]
```

### daily_arxiv_digest_skill

```text
trace.task_type = subscription_run
tags = ["subscription_run", "subscription_id:{id}"]
```

### local_library_manage_skill

```text
trace.task_type = library_manage
tags = ["library", "action:{action}"]
```

### trace_diagnosis_skill

```text
trace.task_type = trace_query
tags = ["trace_query"]
```

---

# 12. Skill 编写统一规范

每个 `SKILL.md` 都应包含以下结构：

```markdown
# Skill Name

## 1. Purpose
这个 Skill 解决什么问题。

## 2. When to Use
什么时候触发。

## 3. Inputs
输入字段。

## 4. Outputs
输出字段。

## 5. Tools
会调用哪些工具。

## 6. Workflow
执行步骤。

## 7. Prompt Rules
提示词规则。

## 8. Quality Checks
质量检查。

## 9. Error Handling
失败处理。

## 10. Trace Logging
如何记录 trace。
```

---

# 13. 具体 SKILL.md 模板

```markdown
# {{skill_name}}

## 1. Purpose

{{purpose}}

## 2. When to Use

Use this skill when:

- {{condition_1}}
- {{condition_2}}

## 3. Inputs

```json
{
  "field": "value"
}
```

## 4. Outputs

```json
{
  "type": "{{output_type}}",
  "trace_id": "trace_xxx",
  "data": {}
}
```

## 5. Tools

This skill may call:

```text
tool.name_1
tool.name_2
tool.name_3
```

## 6. Workflow

```text
1. Step one
2. Step two
3. Step three
```

## 7. Prompt Rules

```text
1. Rule one
2. Rule two
3. Rule three
```

## 8. Quality Checks

```text
1. Check one
2. Check two
3. Check three
```

## 9. Error Handling

```text
Error A:
- handling strategy

Error B:
- handling strategy
```

## 10. Trace Logging

```text
trace.task_type = ""
trace.tags = []
required steps = []
```
```

---

# 14. Skill 开发优先级

## Phase 1

```text
paper_search_card_skill
```

目标：

```text
用户输入“给我找 2 篇关于 agent 的论文”
系统返回论文卡片
```

## Phase 2

```text
paper_deep_parse_skill
```

目标：

```text
用户点击解析
系统生成 report.md
```

## Phase 3

```text
daily_arxiv_digest_skill
```

目标：

```text
系统每天自动推送论文到邮箱 / 飞书
```

## Phase 4

```text
local_library_manage_skill
```

目标：

```text
用户可以通过自然语言管理本地论文库
```

## Phase 5

```text
trace_diagnosis_skill
```

目标：

```text
用户可以通过自然语言查询任务流程和失败原因
```

---

# 15. Skill 验收标准

### paper_search_card_skill

```text
1. 能识别论文搜索请求
2. 能纠正 agnet → agent
3. 能从 candidate_k 中筛选 top_n
4. 能生成中文论文卡片
5. 不做全文解析
6. 能记录 trace
```

### paper_deep_parse_skill

```text
1. 能下载 PDF
2. 能生成 parsed.md
3. 能生成 report.md
4. 能更新本地库状态
5. 能在失败时保留已有文件
6. 能记录 trace
```

### daily_arxiv_digest_skill

```text
1. 能读取订阅配置
2. 能按主题检索论文
3. 能筛选 Top N
4. 能生成每日精选
5. 能自动收藏论文
6. 能发送邮箱
7. 能发送飞书
8. 能记录 subscription_run 和 trace
```

### local_library_manage_skill

```text
1. 能查询本地库
2. 能查看报告
3. 能删除论文
4. 能删除报告
5. 能重新生成报告
6. 能记录 trace
```

### trace_diagnosis_skill

```text
1. 能查询任务历史
2. 能查看任务步骤
3. 能定位失败步骤
4. 能给出错误摘要
5. 不泄露敏感信息
```

---

# 16. Claude 实现 Skill 时的注意事项

Claude 实现 Skill 时必须遵守：

```text
1. 不要把 Skill 写成单个 Prompt
2. Skill 必须有明确输入输出
3. Skill 必须声明调用哪些 Tool
4. Skill 必须有失败处理
5. Skill 必须记录 trace
6. 搜索 Skill 不允许全文解析
7. 每日精选 Skill 默认不全文解析
8. 删除类 Skill 默认 soft delete
9. 不得泄露密钥、webhook、邮箱密码
10. 每完成一个 Skill，需要更新 PROJECT_STATE.md
```

---

# 17. MVP 必须创建的 Skill 文件

第一批至少创建：

```text
skills/
  paper_search_card_skill/
    SKILL.md
    prompts/card_summary_zh.md

  paper_deep_parse_skill/
    SKILL.md
    prompts/deep_report_zh.md

  daily_arxiv_digest_skill/
    SKILL.md
    prompts/daily_digest_zh.md
```

后续再创建：

```text
skills/
  local_library_manage_skill/
    SKILL.md

  trace_diagnosis_skill/
    SKILL.md
```

---

# 18. 总结

本项目 Skill 的核心思想是：

```text
Tool 负责做动作
Skill 负责编排动作
Prompt 负责控制语言输出
Trace 负责记录过程
Memory 负责提供偏好和历史上下文
```

项目最重要的三个 Skill 是：

```text
1. paper_search_card_skill
2. paper_deep_parse_skill
3. daily_arxiv_digest_skill
```

这三个 Skill 跑通后，项目就具备了：

```text
聊天找论文
点击解析论文
每日自动推送论文
```

也就是本项目的核心闭环。

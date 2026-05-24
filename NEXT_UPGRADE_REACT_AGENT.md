# NEXT_UPGRADE_REACT_AGENT.md

# arXiv 论文助手 Agent 下一阶段升级方案

## 1. 文档目的

本文档用于指导 Claude 对当前 arXiv 论文助手 Agent 进行下一阶段架构升级。

当前项目已经具备固定流程式 Agent 的设计基础，包括：

```text
用户意图识别
固定 Orchestrator 流程
Tool 层
Skill 设计文档
MCP 设计文档
Trace 可观测性设计
```

下一阶段目标是：

```text
从“固定编排型 Agent”
升级为
“受控 ReAct + Tool Calling + Skill/MCP 扩展”的 Agent 架构
```

核心目标不是让模型完全自由地乱调用工具，而是让模型在受控边界内具备一定自主规划能力。

---

## 2. 当前架构与目标架构对比

### 2.1 当前架构：固定编排型 Agent

当前流程：

```text
用户输入
  ↓
意图识别
  ↓
Orchestrator 进入固定流程
  ↓
按固定顺序调用 Tool
  ↓
返回结果
```

示例：

```text
用户：给我找 2 篇关于 Agent 的论文

系统固定执行：
intent classify
→ query normalize
→ arxiv search
→ rerank
→ card summary
→ return
```

优点：

```text
稳定
容易调试
业务规则清晰
适合 MVP
```

缺点：

```text
灵活性不足
复杂任务需要写很多 if/else
后续接入 Skill / MCP / 外部工具时扩展成本较高
模型不能根据 observation 动态调整下一步
```

---

### 2.2 目标架构：受控 ReAct Agent

升级后采用受控 ReAct Agent。

目标流程：

```text
用户输入
  ↓
ReAct Agent 规划下一步
  ↓
Tool Calling 调用工具
  ↓
获得 Observation
  ↓
根据 Observation 再决策
  ↓
直到 final_answer 或达到 max_steps
```

但必须注意：

```text
不是完全自由 Agent
而是 Controlled ReAct Agent
```

模型只能从系统注册过的 Tool / Skill / MCP 能力中选择 action。

每一步都必须经过：

```text
工具白名单校验
权限等级校验
状态机校验
业务规则校验
Trace 记录
max_steps 限制
```

---

## 3. 核心架构关键词

本次升级的核心架构关键词：

```text
Controlled ReAct Agent
Tool Registry
Skill-as-Tool
MCP Adapter
Trace-first Observability
State-guarded Tool Calling
Permission-aware Tool Execution
```

---

## 4. 为什么项目适合升级为 ReAct Agent

当前项目已经具备天然基础。

### 4.1 已经有 Tool 层

当前已有或规划中的 Tool 包括：

```text
ArxivTool
RerankTool
ReportTool
PdfTool
LibraryTool
TraceTool
SubscriptionTool
NotifyTool
```

这些 Tool 可以进一步注册到 Tool Registry 中，变成模型可调用的 function schema。

### 4.2 已经有 Orchestrator

当前的 `orchestrator.py` 负责固定流程编排。

后续可以演进为：

```text
ReactAgent
```

原有固定流程可以保留为 Skill，作为高级 Tool 被 ReAct Agent 调用。

### 4.3 已经有 Trace

ReAct 最大的问题是黑盒。

本项目已经设计了：

```text
tasks
task_steps
trace_id
step_name
input_summary
output_summary
status
duration_ms
error_message
```

因此可以把每次 ReAct 过程记录为：

```text
reasoning_summary
action
arguments
observation
status
```

这样既能使用 ReAct，又不失去可观测性。

### 4.4 已经有 Skill 和 MCP 设计文档

已有：

```text
SKILLS.md
MCP.md
```

这两个文档已经定义了：

```text
Tool 和 Skill 的边界
MCP Tools
MCP Resources
MCP Prompts
Skill 工作流
```

下一阶段只需要代码落地。

---

## 5. 推荐目标架构

推荐升级为四层结构：

```text
ReactAgent
  ↓
Tool Registry
  ↓
Skill Registry / MCP Adapter
  ↓
已有业务 Tool / Service
```

---

## 6. 四层架构说明

### 6.1 ReactAgent

职责：

```text
1. 接收用户输入
2. 读取当前任务状态
3. 读取可用工具列表
4. 决定下一步 action
5. 调用 Tool Registry
6. 接收 observation
7. 判断是否继续执行
8. 生成 final_answer
```

ReactAgent 不直接操作数据库、不直接下载文件、不直接请求 arXiv。

它只负责：

```text
决策
规划
选择工具
整合结果
```

### 6.2 Tool Registry

职责：

```text
1. 注册所有可调用 Tool
2. 为每个 Tool 提供 function schema
3. 根据工具名找到 handler
4. 校验工具是否允许被当前任务调用
5. 执行工具
6. 返回标准 observation
```

Tool Registry 是 ReAct 的安全边界之一。

### 6.3 Skill Registry

职责：

```text
1. 把稳定工作流包装成高级 Tool
2. 让 ReAct Agent 可以直接调用 Skill
3. 避免模型自由拼接过多底层 Tool
```

示例：

```text
paper_search_card_skill
paper_deep_parse_skill
daily_arxiv_digest_skill
trace_diagnosis_skill
```

对于模型来说，Skill 也可以被当成 Tool。

这就是：

```text
Skill-as-Tool
```

### 6.4 MCP Adapter

职责：

```text
1. 把本项目能力暴露为 MCP Server

```

建议优先实现：

```text
本项目作为 MCP Server
```

因为这更贴合当前已有的 `MCP.md`。

---

## 7. ReAct Loop 设计

### 7.1 基本流程

一次 ReAct 循环如下：

```text
1. 模型读取用户输入、当前任务状态、可用工具列表
2. 模型输出下一步决策
3. 后端校验 action 是否允许
4. 后端调用 Tool
5. 得到 observation
6. 写入 trace step
7. observation 加入 agent_state
8. 模型继续判断下一步
9. 达到 final_answer 或 max_steps 后结束
```

### 7.2 模型输出格式

禁止暴露完整思维链。

模型只输出简短的 `reasoning_summary`。

推荐结构：

```json
{
  "reasoning_summary": "用户想搜索论文，当前需要先调用论文搜索技能。",
  "action": "paper_search_card_skill",
  "arguments": {
    "topic": "agent",
    "top_n": 2,
    "candidate_k": 20
  }
}
```

如果任务已完成：

```json
{
  "reasoning_summary": "已完成论文检索并生成卡片，可以返回结果。",
  "action": "final_answer",
  "final_answer": {
    "type": "paper_search_result",
    "papers": []
  }
}
```

### 7.3 不要记录完整思维链

Trace 中只能记录：

```text
reasoning_summary
action
arguments 摘要
observation 摘要
status
duration
error
```

不要记录：

```text
完整 chain of thought
完整系统 Prompt
完整工具返回正文
敏感密钥
```

### 7.4 ReAct 伪代码

```python
async def run_react_agent(message: str, session_id: str):
    trace = await trace_service.create(
        task_type="react_agent",
        user_input=message,
    )

    state = AgentState(
        user_message=message,
        session_id=session_id,
        observations=[],
        max_steps=6,
    )

    allowed_tools = tool_registry.get_allowed_tools_for_message(message)

    for step in range(state.max_steps):
        decision = await llm_client.plan_with_tools(
            user_message=message,
            state=state.to_summary(),
            tools=allowed_tools,
        )

        await trace_service.log_step(
            trace_id=trace.trace_id,
            step_name="agent_decision",
            input_summary=state.to_summary(),
            output_summary={
                "reasoning_summary": decision.reasoning_summary,
                "action": decision.action,
            },
        )

        if decision.action == "final_answer":
            await trace_service.mark_success(trace.trace_id)
            return decision.final_answer

        validate_tool_call(
            action=decision.action,
            arguments=decision.arguments,
            state=state,
            allowed_tools=allowed_tools,
        )

        observation = await tool_registry.call(
            decision.action,
            decision.arguments,
            trace_id=trace.trace_id,
        )

        await trace_service.log_step(
            trace_id=trace.trace_id,
            step_name=decision.action,
            tool_name=decision.action,
            input_summary=safe_summary(decision.arguments),
            output_summary=safe_summary(observation),
            status=observation.status,
        )

        state.add_observation(observation)

        if observation.status == "failed":
            return await handle_failed_observation(trace, state, observation)

    await trace_service.mark_failed(
        trace.trace_id,
        error_message="ReAct reached max_steps without final answer",
    )

    return {
        "type": "error",
        "message": "任务执行步骤过多，已停止。请缩小问题范围后重试。",
        "trace_id": trace.trace_id,
    }
```

---

## 8. Tool Calling 升级方案

### 8.1 当前问题

当前 `llm_client.py` 可能只有：

```text
chat()
chat_json()
```

下一步需要新增：

```text
chat_with_tools()
plan_with_tools()
```

### 8.2 推荐 Tool Schema

```json
{
  "type": "function",
  "function": {
    "name": "arxiv_search",
    "description": "Search arXiv papers by query",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search query"
        },
        "max_results": {
          "type": "integer",
          "description": "Maximum number of candidate papers"
        }
      },
      "required": ["query"]
    }
  }
}
```

### 8.3 需要注册的基础 Tool

第一批注册：

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
trace_query
```

第二批注册：

```text
library_add_paper
paper_download_pdf
pdf_parse_full_text
paper_generate_deep_report
subscription_create
subscription_run
```

第三批注册：

```text
email_send
feishu_send
library_delete_paper
library_delete_report
mcp_external_tool
```

---

## 9. Tool Registry 设计

### 9.1 新增文件

```text
backend/app/agent/tool_registry.py
backend/app/agent/tool_schemas.py
```

### 9.2 ToolDefinition 数据结构

```python
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal

ToolPermission = Literal[
    "read_only",
    "write_safe",
    "write_dangerous",
    "expensive",
    "external_send",
]

@dataclass
class ToolDefinition:
    name: str
    description: str
    schema: dict
    handler: Callable[..., Awaitable[dict]]
    allowed_intents: list[str]
    permission: ToolPermission
    requires_confirmation: bool = False
```

### 9.3 ToolRegistry 示例

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_schemas(self, intent: str | None = None) -> list[dict]:
        tools = self._tools.values()
        if intent:
            tools = [
                t for t in tools
                if intent in t.allowed_intents or "*" in t.allowed_intents
            ]
        return [t.schema for t in tools]

    async def call(self, name: str, arguments: dict, context: dict) -> dict:
        tool = self.get(name)
        validate_permission(tool, context)
        validate_business_rules(tool, arguments, context)
        return await tool.handler(**arguments)
```

### 9.4 Tool 权限等级

建议给 Tool 加权限等级。

```text
read_only:
  arxiv_search
  library_search
  trace_query

write_safe:
  collect_paper
  create_subscription

write_dangerous:
  delete_paper
  delete_report

expensive:
  pdf_parse_full_text
  deep_report_generation

external_send:
  email_send
  feishu_send
```

---

## 10. 受控 ReAct 的业务规则

必须保留以下产品规则。

### 10.1 搜索阶段不允许全文解析

规则：

```text
如果当前 intent = paper_search
禁止调用：
pdf_parse_full_text
paper_generate_deep_report
```

允许调用：

```text
arxiv_search
paper_rerank
paper_generate_card_summary
paper_search_card_skill
```

### 10.2 收藏和解析必须分开

规则：

```text
收藏只能下载 PDF 和保存 metadata
解析才允许全文解析和生成 report.md
```

禁止：

```text
用户只点收藏时，偷偷调用 pdf_parse_full_text
```

### 10.3 删除默认 soft delete

规则：

```text
delete_paper 默认 mode = soft
hard delete 必须二次确认
```

### 10.4 订阅默认不全文解析

规则：

```text
subscription_create 默认 auto_parse_full_text = false
```

除非用户明确要求：

```text
每天自动精读
每天生成全文解析报告
```

### 10.5 所有副作用操作必须 trace

副作用操作包括：

```text
收藏论文
解析论文
删除论文
删除报告
创建订阅
修改订阅
删除订阅
发送邮件
发送飞书
```

这些操作必须写入 trace。

### 10.6 max_steps 限制

建议：

```text
max_steps = 6
```

如果超过限制，终止并返回用户可理解提示。

### 10.7 敏感信息不能进入 trace

Trace 中不得出现：

```text
API Key
邮箱密码
飞书 webhook 明文
完整 Prompt
完整 PDF 正文
```

---

## 11. Skill-as-Tool 设计

### 11.1 为什么 Skill 要包装成 Tool

不建议一开始让模型自由拼接所有底层 Tool。

错误示例：

```text
模型自己决定：
arxiv_search
→ paper_rerank
→ paper_generate_card_summary
→ pdf_parse_full_text
```

这样容易导致：

```text
搜索阶段偷偷全文解析
跳过 trace
参数乱传
步骤过多
业务规则失控
```

更稳的方式：

```text
把稳定流程包装成高级 Tool
```

例如：

```text
paper_search_card_skill
```

内部固定执行：

```text
intent/query normalize
→ arxiv search
→ rerank
→ card summary
```

对 ReAct Agent 来说，它只是一个可调用 Tool。

---

### 11.2 第一批 Skill Tool

第一批注册：

```text
paper_search_card_skill
trace_diagnosis_skill
local_library_manage_skill
```

第二批注册：

```text
paper_deep_parse_skill
daily_arxiv_digest_skill
```

### 11.3 paper_search_card_skill Schema

```json
{
  "type": "function",
  "function": {
    "name": "paper_search_card_skill",
    "description": "Search arXiv papers and generate Chinese paper cards based on title, abstract, and optional introduction.",
    "parameters": {
      "type": "object",
      "properties": {
        "user_message": {
          "type": "string"
        },
        "topic": {
          "type": "string"
        },
        "top_n": {
          "type": "integer",
          "default": 2
        },
        "candidate_k": {
          "type": "integer",
          "default": 20
        }
      },
      "required": ["user_message", "topic"]
    }
  }
}
```

### 11.4 paper_deep_parse_skill Schema

```json
{
  "type": "function",
  "function": {
    "name": "paper_deep_parse_skill",
    "description": "Download a paper PDF, parse full text, and generate a Chinese deep reading report.",
    "parameters": {
      "type": "object",
      "properties": {
        "arxiv_id": {
          "type": "string"
        },
        "pdf_url": {
          "type": "string"
        },
        "user_research_direction": {
          "type": "string"
        }
      },
      "required": ["arxiv_id", "pdf_url"]
    }
  }
}
```

权限：

```text
expensive
```

只允许在：

```text
paper_parse
report_regenerate
subscription_run with auto_parse_full_text = true
```

中调用。

---

## 12. MCP 接入设计

MCP 有两个方向。

### 12.1 本项目作为 MCP Server

把本项目能力暴露给：

```text
Claude
Cursor
ChatGPT
其他外部 Agent
```

示例：

```text
mcp tool: arxiv.search_papers
mcp tool: paper.generate_deep_report
mcp resource: library://paper/{arxiv_id}/report
mcp prompt: paper/card_summary_zh
```

建议优先做这个方向。

原因：

```text
1. 与 MCP.md 一致
2. 能展示项目工程化能力
3. 可在面试中说明项目可被外部 Agent 调用
```

### 12.2 本项目作为 MCP Client

后续可让本项目 Agent 调用外部 MCP：

```text
文件系统 MCP
Zotero MCP
Notion MCP
浏览器 MCP
数据库 MCP
```

这属于后续增强，不是当前优先级,不做。

### 12.3 MCP Server 新增目录

```text
backend/mcp_server/
  server.py
  tools/
    arxiv_tools.py
    paper_tools.py
    library_tools.py
    subscription_tools.py
    trace_tools.py
  resources/
    library_resources.py
    trace_resources.py
  prompts/
    paper_prompts.py
    digest_prompts.py
```

要求：

```text
MCP tools 复用已有 service/tool
不要复制业务逻辑
```

---

## 13. Trace-first Observability 设计

### 13.1 ReAct Trace Step

每一步记录：

```json
{
  "trace_id": "trace_xxx",
  "step_name": "react_step_1",
  "tool_name": "paper_search_card_skill",
  "reasoning_summary": "用户想搜索论文，因此调用论文搜索技能。",
  "input_summary": {
    "topic": "agent",
    "top_n": 2
  },
  "output_summary": {
    "papers_count": 2,
    "status": "success"
  },
  "status": "success",
  "duration_ms": 2100
}
```

### 13.2 ReAct 失败记录

示例：

```json
{
  "trace_id": "trace_xxx",
  "step_name": "react_step_3",
  "tool_name": "pdf_parse_full_text",
  "reasoning_summary": "用户要求解析论文，需要解析 PDF 全文。",
  "status": "failed",
  "error_message": "PDF_PARSE_FAILED"
}
```

### 13.3 Trace 页面升级

前端 Trace 页面可以增加：

```text
ReAct 步骤
Reasoning Summary
Action
Observation
Tool Permission
是否通过业务规则校验
```

不要展示完整思维链。

---

## 14. 推荐落地顺序

不要一次性大改。

建议分四步。

### 14.1 第一步：Tool Registry

新增：

```text
backend/app/agent/tool_registry.py
backend/app/agent/tool_schemas.py
```

目标：

```text
把现有 Tool 包装成统一接口
提供 tool schema
提供权限等级
提供 allowed_intents
提供统一 call 方法
```

第一批注册：

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
trace_query
```

验收：

```text
可以通过 Tool Registry 调用 arxiv_search
可以列出 tools schema
可以根据 intent 过滤工具
权限字段存在
```

### 14.2 第二步：ReAct Agent MVP

新增：

```text
backend/app/agent/react_agent.py
```

先只支持三个能力：

```text
paper_search
library_search
trace_search
```

不要一上来支持：

```text
收藏
删除
解析
订阅创建
邮件发送
飞书发送
```

原因：

```text
这些都是有副作用或高成本操作，需要先跑通 read_only ReAct
```

验收：

```text
用户输入“给我找 2 篇关于 agent 的论文”
ReAct Agent 能调用 paper_search_card_skill
返回论文卡片
Trace 中能看到 reasoning_summary/action/observation
```

### 14.3 第三步：Skill Registry

新增：

```text
backend/app/agent/skill_registry.py
```

把这些包装成高级工具：

```text
paper_search_card_skill
paper_deep_parse_skill
daily_arxiv_digest_skill
trace_diagnosis_skill
local_library_manage_skill
```

优先落地：

```text
paper_search_card_skill
trace_diagnosis_skill
```

验收：

```text
Skill 可以像 Tool 一样被调用
Skill 内部仍走固定安全流程
Skill 调用过程写入 trace
```

### 14.4 第四步：MCP Server

新增：

```text
backend/mcp_server/
```

目标：

```text
把本项目能力暴露为 MCP Server
```

优先暴露：

```text
arxiv.search_papers
library.search_papers
library.get_report
trace.query
```

验收：

```text
外部 MCP Client 可以调用项目搜索论文
外部 MCP Client 可以读取本地报告
MCP tools 复用已有 service
```

---

## 15. Claude 实施任务清单

### 15.1 任务 1：实现 Tool Registry

创建文件：

```text
backend/app/agent/tool_registry.py
backend/app/agent/tool_schemas.py
```

实现：

```text
ToolDefinition
ToolRegistry
register
get
list_schemas
call
permission 校验
allowed_intents 过滤
```

### 15.2 任务 2：接入现有 Tool

注册：

```text
arxiv_search
paper_rerank
paper_generate_card_summary
library_search_papers
trace_query
```

要求：

```text
复用现有 service/tool
不要复制业务逻辑
```

### 15.3 任务 3：实现 chat_with_tools

修改：

```text
backend/app/core/llm_client.py
```

新增：

```text
chat_with_tools()
plan_with_tools()
```

要求输出结构：

```json
{
  "reasoning_summary": "",
  "action": "",
  "arguments": {}
}
```

### 15.4 任务 4：实现 ReAct Agent MVP

创建：

```text
backend/app/agent/react_agent.py
```

支持：

```text
paper_search
library_search
trace_search
```

限制：

```text
max_steps = 6
只允许 read_only 工具
不允许删除、解析、发送
```

### 15.5 任务 5：升级 Orchestrator

修改：

```text
backend/app/agent/orchestrator.py
```

策略：

```text
简单稳定任务仍可走固定流程
需要动态规划的任务走 ReactAgent
```

初期可配置：

```text
USE_REACT_AGENT=true
```

### 15.6 任务 6：实现 Skill Registry

创建：

```text
backend/app/agent/skill_registry.py
```

注册：

```text
paper_search_card_skill
trace_diagnosis_skill
```

### 15.7 任务 7：升级 Trace

给 `task_steps` 增加或复用字段：

```text
reasoning_summary
tool_name
input_summary
output_summary
status
duration_ms
error_message
```

如果不改表结构，也可以把 `reasoning_summary` 放进 `output_summary` JSON。

### 15.8 任务 8：更新前端 Trace 页面

展示：

```text
ReAct Step
Reasoning Summary
Action
Observation Summary
Status
Duration
Error
```

---

## 16. 安全边界总表

| 规则 | 要求 |
|---|---|
| 搜索阶段 | 禁止全文解析 |
| 收藏 | 只下载 PDF 和 metadata |
| 解析 | 才允许 parse_full_text 和 report |
| 删除 | 默认 soft delete |
| 订阅 | 默认 auto_parse_full_text = false |
| 副作用操作 | 必须 trace |
| Tool 调用 | 必须白名单校验 |
| ReAct 步数 | max_steps = 6 |
| 敏感信息 | 不进入 trace |
| 思维链 | 不暴露，只记录 reasoning_summary |

---

## 17. 面试表达版本

可以这样介绍这次升级：

```text
我把当前固定 Orchestrator 演进成了受控 ReAct Agent。
模型不再只是被动进入固定流程，而是可以根据任务状态选择下一步 action。
但所有 action 都来自 Tool Registry，并经过权限、状态机和业务规则校验。

底层 Tool 负责原子能力，例如 arXiv 检索、PDF 下载、全文解析、本地库查询。
Skill 负责稳定工作流，例如论文搜索卡片生成、论文全文解析、每日订阅推送。
MCP Adapter 则负责把项目能力标准化暴露给 Claude、Cursor 等外部 Agent。

为了避免 Agent 黑盒化，我采用 Trace-first Observability。
每一次 reasoning_summary、action、arguments、observation 都会进入 trace。
这样既保留 Agent 的灵活性，又避免模型乱调工具、偷偷全文解析、跳过 trace 等不可控问题。
```

---

## 18. 最终升级目标

升级完成后，项目将从：

```text
普通论文 CRUD + 固定 API 调用系统
```

升级为：

```text
可观测、可扩展、可控的科研 Agent 系统
```

具备以下能力：

```text
1. 模型可以在安全边界内自主选择下一步工具
2. 所有工具通过 Tool Registry 管理
3. 稳定流程通过 Skill-as-Tool 调用
4. MCP 作为外部扩展接口
5. 所有过程可追踪、可诊断、可回放
```

最终架构关键词：

```text
Controlled ReAct Agent
Tool Registry
Skill-as-Tool
MCP Adapter
Trace-first Observability
State-guarded Tool Calling
```

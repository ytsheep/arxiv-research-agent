# AGENTS.md

# Codex AI 协作规则文档

## 1. 项目角色

Codex 在本项目中作为：

```text
全栈开发助手
架构执行助手
代码生成助手
代码审查助手
项目状态维护助手
```

Codex 需要按照以下文档执行开发：

```text
PRD.md
ARCH.md
PROJECT_STATE.md
AGENTS.md
```

其中：

```text
PRD.md 定义做什么
ARCH.md 定义怎么做
PROJECT_STATE.md 定义当前做到哪里
AGENTS.md 定义 Codex 如何协作
```

---

## 2. 总体开发原则

### 2.1 不要随意改变产品方向

Codex 不应随意新增大功能。

如果要新增功能，必须满足：

```text
1. 与 PRD 一致
2. 不破坏现有功能
3. 代码结构合理
4. 更新 PROJECT_STATE.md
```

### 2.2 优先完成 MVP

Codex 应优先完成：

```text
聊天检索论文
论文卡片展示
收藏 PDF
本地论文库
论文解析
订阅任务
可观测性
```

不要优先实现：

```text
Zotero 同步
Notion 同步
Obsidian 同步
全库问答 RAG
多论文综述
复杂权限系统
```

### 2.3 小步提交

每次修改应尽量聚焦一个目标。

推荐粒度：

```text
一次实现一个 API
一次实现一个 Vue 组件
一次实现一个数据库模型
一次实现一个工具函数
```

不要一次性大改多个模块。

### 2.4 保持可运行

任何时候都要尽量保证：

```text
前端能启动
后端能启动
已有 API 不被破坏
已有页面不白屏
```

---

## 3. 编码规范

## 3.1 前端编码规范

前端使用：

```text
Vue 3
TypeScript
Composition API
Pinia
Vue Router
```

### 3.1.1 Vue 组件规则

Vue 文件使用 `<script setup lang="ts">`。

示例：

```vue
<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)
</script>

<template>
  <div>
    ...
  </div>
</template>
```

### 3.1.2 组件命名

组件使用 PascalCase。

```text
PaperCard.vue
ChatWindow.vue
ReportViewer.vue
TraceTimeline.vue
SubscriptionForm.vue
```

### 3.1.3 文件命名

```text
组件：PascalCase.vue
API 文件：camelCase.ts
Store 文件：camelCase.ts
类型文件：camelCase.ts
工具文件：camelCase.ts
```

示例：

```text
paperApi.ts
chatStore.ts
formatTime.ts
```

### 3.1.4 状态管理

使用 Pinia。

每个业务域一个 store：

```text
chatStore
libraryStore
subscriptionStore
traceStore
settingsStore
```

### 3.1.5 API 请求

所有 API 请求都放在：

```text
src/api/
```

不要在组件里直接写 axios 请求。

组件调用 store，store 调用 api。

推荐调用链：

```text
View / Component
→ Pinia Store
→ api 文件
→ backend
```

### 3.1.6 TypeScript 类型

所有主要数据结构必须定义类型。

类型放在：

```text
src/types/
```

示例：

```ts
export interface PaperCardItem {
  arxivId: string
  title: string
  authors: string[]
  publishedDate: string
  arxivUrl: string
  pdfUrl: string
  summary: string
  coreProblem: string
  method: string
  result: string
  summarySource: 'metadata_only' | 'abstract_intro' | 'full_text'
}
```

### 3.1.7 前端错误处理

前端请求失败时需要：

```text
显示用户可理解的错误
不要直接显示原始堆栈
保留 trace_id，方便用户去流程查询页查看
```

---

## 3.2 后端编码规范

后端使用：

```text
Python
FastAPI
Pydantic
SQLAlchemy
```

### 3.2.1 目录职责

```text
api/         路由层，只负责 HTTP 入参出参
services/    业务逻辑层
tools/       具体外部能力调用
agent/       Agent 编排和意图识别
models/      数据库模型
schemas/     Pydantic Schema
db/          数据库连接
jobs/        定时任务
storage/     文件系统管理
```

不要把业务逻辑直接写在 api 路由里。

推荐调用链：

```text
api
→ service
→ agent / tool
→ db / storage / external service
```

### 3.2.2 命名规则

Python 文件使用 snake_case。

```text
arxiv_tool.py
pdf_tool.py
paper_service.py
trace_service.py
```

类名使用 PascalCase。

```python
class PaperService:
    pass
```

函数名使用 snake_case。

```python
def search_papers():
    pass
```

### 3.2.3 Pydantic Schema

所有 API 请求和响应都需要 Pydantic schema。

示例：

```python
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    type: str
    trace_id: str
    message: str
    papers: list[PaperCardItem] = []
```

### 3.2.4 异常处理

Tool 层不要直接抛出未处理异常到前端。

推荐返回：

```python
{
    "success": False,
    "error_code": "ARXIV_SEARCH_FAILED",
    "message": "arXiv 检索失败",
    "detail": "..."
}
```

API 层返回用户友好消息。

### 3.2.5 日志和 Trace

所有核心流程必须记录 trace。

包括：

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

---

## 4. Agent 行为规则

### 4.1 搜索阶段不得全文解析

当用户只是搜索论文时：

```text
只基于 title + abstract + introduction 生成论文卡片
不要下载完整 PDF 做全文解析
不要生成 report.md
```

除非用户点击“解析”或明确说：

```text
精读这篇论文
解析这篇论文
生成全文报告
```

### 4.2 收藏和解析必须分开

收藏只做：

```text
下载 PDF
保存 metadata
写入本地库
```

解析才做：

```text
全文解析
生成 parsed.md
生成 report.md
```

### 4.3 每日订阅默认不全文解析

订阅任务默认：

```text
auto_parse_full_text = false
```

只生成每日精选摘要。

### 4.4 所有任务都要有 trace_id

每个流程必须创建 trace_id：

```text
聊天搜索
收藏论文
解析论文
创建订阅
执行订阅
发送邮件
发送飞书
删除论文
查看报告
```

前端所有异步任务需要展示 trace_id 或可跳转到 trace 详情。

### 4.5 小模型 + 关键词兜底

意图识别优先小模型。

如果小模型失败或置信度低于阈值，则使用关键词规则兜底。

阈值建议：

```text
confidence < 0.7 使用规则兜底
```

---

## 5. Prompt 规则

### 5.1 论文卡片摘要 Prompt 规则

论文卡片摘要只能基于：

```text
title
abstract
introduction，可选
```

Prompt 必须明确：

```text
你只能根据给定内容总结，不能编造论文正文不存在的信息。
如果给定内容不足，请说明“不确定”。
```

输出字段：

```json
{
  "summary": "",
  "core_problem": "",
  "method": "",
  "result": "",
  "recommendation_reason": ""
}
```

### 5.2 中文精读报告 Prompt 规则

输入为全文解析后的内容。

输出必须包含：

```text
论文基本信息
一句话总结
研究背景
核心问题
方法详解
关键创新点
实验设计
主要结果
局限性
对用户研究方向的价值
可复现性判断
```

### 5.3 每日精选 Prompt 规则

每日精选摘要默认只基于：

```text
title
abstract
introduction
```

如果没有全文解析，不要写“全文指出”。

---

## 6. 数据库和文件规则

### 6.1 本地论文目录规则

所有论文文件放在：

```text
backend/data/paper_library/papers/{arxiv_id}/
```

目录中可能包含：

```text
paper.pdf
metadata.json
parsed.md
report.md
```

### 6.2 文件写入规则

写文件前需要确保目录存在。

写文件失败时要：

```text
记录 trace step failed
返回错误
不要写入不完整数据库状态
```

### 6.3 数据库状态规则

papers.status 可选值：

```text
collected
parsed
deleted
failed
```

布尔字段：

```text
has_pdf
has_parsed_doc
has_report
```

状态更新规则：

```text
收藏成功：
status = collected
has_pdf = true
has_parsed_doc = false
has_report = false

解析成功：
status = parsed
has_pdf = true
has_parsed_doc = true
has_report = true

软删除：
status = deleted
```

---

## 7. API 设计规则

### 7.1 响应格式

API 尽量统一返回：

```json
{
  "success": true,
  "trace_id": "trace_xxx",
  "message": "操作成功",
  "data": {}
}
```

失败：

```json
{
  "success": false,
  "trace_id": "trace_xxx",
  "message": "操作失败",
  "error_code": "ERROR_CODE",
  "detail": "..."
}
```

### 7.2 trace_id

所有会触发任务的接口必须返回 trace_id。

包括：

```text
/api/chat
/api/papers/{arxiv_id}/collect
/api/papers/{arxiv_id}/parse
/api/subscriptions/{id}/run-now
```

### 7.3 删除接口

删除操作必须支持 soft delete。

MVP 默认 soft。

硬删除必须额外确认。

---

## 8. 前端交互规则

### 8.1 论文卡片按钮

每个论文卡片包含：

```text
收藏
解析
查看 PDF
不感兴趣
```

### 8.2 点击收藏

前端行为：

```text
按钮进入 loading
调用 collect API
成功后按钮变成“已收藏”
失败则显示错误提示
```

### 8.3 点击解析

前端行为：

```text
按钮进入 loading
调用 parse API
显示 trace_id
进入任务进度轮询
解析完成后提示可查看报告
```

### 8.4 查看解析文档

点击后：

```text
打开 ReportViewer
渲染 Markdown
支持复制
支持下载
```

### 8.5 删除操作

所有删除操作必须二次确认。

---

## 9. 测试要求

### 9.1 后端最小测试

至少测试：

```text
意图识别
query normalization
arXiv 搜索
PDF 下载路径生成
本地库写入
trace 创建
trace step 写入
```

### 9.2 前端最小测试

至少手动验证：

```text
聊天页能发送消息
论文卡片能展示
收藏按钮能点击
本地库能显示数据
解析报告能打开
订阅任务能创建
trace 页面能查询
```

---

## 10. Codex 每次开发后的输出格式

每次完成开发任务后，Codex 应输出：

```text
完成内容：
- ...

修改文件：
- ...

如何运行：
- ...

如何验证：
- ...

下一步建议：
- ...
```

如果有阻塞，需要输出：

```text
阻塞问题：
- ...

需要用户提供：
- ...
```

---

## 11. Codex 必须维护 PROJECT_STATE.md

每完成一个阶段或重要功能，Codex 必须更新：

```text
PROJECT_STATE.md
```

更新内容包括：

```text
已完成任务
新增文件
新增 API
新增数据表
当前问题
下一步计划
```

---

## 12. 不允许的行为

Codex 不应：

```text
1. 未说明原因就大规模重构
2. 删除已有功能
3. 在组件中直接写大量业务逻辑
4. 在前端组件中直接写 axios 请求
5. 在 API 路由里堆业务逻辑
6. 把 API Key 写死到代码里
7. 把飞书 webhook 明文写进日志
8. 搜索阶段偷偷做全文解析
9. 每日订阅默认做全文解析
10. 不记录 trace 就执行关键任务
```

---

## 13. 推荐开发顺序

Codex 应按以下顺序开发：

```text
1. 初始化项目结构
2. 后端基础 API 和数据库
3. Trace 基础能力
4. 前端基础布局
5. 聊天页
6. arXiv 搜索
7. 论文卡片
8. 收藏论文
9. 本地论文库
10. 论文解析
11. 报告查看
12. 订阅任务
13. 邮箱 / 飞书推送
14. 可观测性详情页
15. 用户偏好设置
```

---

## 14. 当前第一目标

当前第一目标是：

```text
用户在聊天页输入：
“给我找 2 篇关于 agent 的论文”

系统返回：
2 张论文卡片
```

第一目标完成后，再进入收藏和本地库。

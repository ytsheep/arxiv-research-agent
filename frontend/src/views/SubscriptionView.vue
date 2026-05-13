<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSubscriptionStore } from '../stores/subscriptionStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { SubscriptionItem } from '../types/subscription'

const store = useSubscriptionStore()
const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref(0)
const deleting = ref<Set<number>>(new Set())

const defaultForm = {
  name: '',
  topics: [] as string[],
  categories: [] as string[],
  candidateK: 20,
  topN: 2,
  cronExpr: '0 8 * * *',
  timezone: 'Asia/Shanghai',
  emailEnabled: false,
  emailTo: '',
  feishuEnabled: false,
  feishuWebhookRef: '',
  autoParseFullText: false,
}

const form = reactive({ ...defaultForm })
const topicInput = ref('')
const categoryInput = ref('')

onMounted(() => {
  store.fetchSubscriptions()
})

function openCreate() {
  isEdit.value = false
  Object.assign(form, defaultForm)
  topicInput.value = ''
  categoryInput.value = ''
  showDialog.value = true
}

function openEdit(sub: SubscriptionItem) {
  isEdit.value = true
  editingId.value = sub.id
  Object.assign(form, {
    name: sub.name,
    topics: [...sub.topics],
    categories: [...sub.categories],
    candidateK: sub.candidateK,
    topN: sub.topN,
    cronExpr: sub.cronExpr,
    timezone: sub.timezone,
    emailEnabled: sub.emailEnabled,
    emailTo: sub.emailTo,
    feishuEnabled: sub.feishuEnabled,
    feishuWebhookRef: sub.feishuWebhookRef,
    autoParseFullText: sub.autoParseFullText,
  })
  topicInput.value = ''
  categoryInput.value = ''
  showDialog.value = true
}

function addTopic() {
  const v = topicInput.value.trim()
  if (v && !form.topics.includes(v)) {
    form.topics.push(v)
  }
  topicInput.value = ''
}

function removeTopic(idx: number) {
  form.topics.splice(idx, 1)
}

function addCategory() {
  const v = categoryInput.value.trim()
  if (v && !form.categories.includes(v)) {
    form.categories.push(v)
  }
  categoryInput.value = ''
}

function removeCategory(idx: number) {
  form.categories.splice(idx, 1)
}

async function handleSave() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入订阅名称')
    return
  }
  if (form.topics.length === 0) {
    ElMessage.warning('请添加至少一个研究主题')
    return
  }

  const data: Partial<SubscriptionItem> = {
    name: form.name.trim(),
    topics: form.topics,
    categories: form.categories,
    candidateK: form.candidateK,
    topN: form.topN,
    cronExpr: form.cronExpr,
    timezone: form.timezone,
    emailEnabled: form.emailEnabled,
    emailTo: form.emailTo,
    feishuEnabled: form.feishuEnabled,
    feishuWebhookRef: form.feishuWebhookRef,
    autoParseFullText: form.autoParseFullText,
  }

  let result
  if (isEdit.value) {
    result = await store.updateSubscription(editingId.value, data)
  } else {
    result = await store.createSubscription(data)
  }

  if (result?.success) {
    ElMessage.success(isEdit.value ? '订阅已更新' : '订阅已创建')
    showDialog.value = false
  } else {
    ElMessage.error(result?.message || '操作失败')
  }
}

async function handleDelete(sub: SubscriptionItem) {
  try {
    await ElMessageBox.confirm(
      `确定删除订阅 "${sub.name}" 吗？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  deleting.value.add(sub.id)
  const result = await store.deleteSubscription(sub.id)
  deleting.value.delete(sub.id)

  if (result.success) {
    ElMessage.success('订阅已删除')
  } else {
    ElMessage.error(result.message || '删除失败')
  }
}

async function handleRunNow(sub: SubscriptionItem) {
  const result = await store.runNow(sub.id)
  if (result?.success) {
    ElMessage.success(
      `执行完成！找到 ${result.paper_count} 篇论文，trace: ${result.trace_id}`
    )
  } else {
    ElMessage.error(result?.message || '执行失败')
  }
}

function cronDescription(cron: string): string {
  const parts = cron.split(' ')
  if (parts.length === 5) {
    return `每天 ${parts[1]}:${parts[0].padStart(2, '0')}`
  }
  return cron
}
</script>

<template>
  <div class="subscription-view">
    <div class="view-header">
      <h1>订阅任务</h1>
      <el-button type="primary" @click="openCreate">创建订阅</el-button>
    </div>

    <el-empty
      v-if="!store.loading && store.subscriptions.length === 0"
      description="暂无订阅任务，点击上方按钮创建"
    >
      <template #image>
        <el-icon :size="60" color="#666"><Bell /></el-icon>
      </template>
    </el-empty>

    <div v-else class="sub-list">
      <el-card
        v-for="sub in store.subscriptions"
        :key="sub.id"
        class="sub-card"
        :body-style="{ padding: '16px' }"
      >
        <div class="sub-card-header">
          <div class="sub-info">
            <h3>{{ sub.name }}</h3>
            <el-tag :type="sub.enabled ? 'success' : 'info'" size="small">
              {{ sub.enabled ? '启用' : '禁用' }}
            </el-tag>
            <span class="sub-cron">{{ cronDescription(sub.cronExpr) }}</span>
          </div>
          <div class="sub-actions">
            <el-button size="small" text type="primary" @click="openEdit(sub)">编辑</el-button>
            <el-button
              size="small"
              text
              type="success"
              :loading="store.running.has(sub.id)"
              @click="handleRunNow(sub)"
            >
              立即运行
            </el-button>
            <el-button
              size="small"
              text
              type="danger"
              :loading="deleting.has(sub.id)"
              @click="handleDelete(sub)"
            >
              删除
            </el-button>
          </div>
        </div>

        <div class="sub-details">
          <div class="detail-row">
            <span class="label">主题：</span>
            <el-tag v-for="t in sub.topics" :key="t" size="small" class="topic-tag">
              {{ t }}
            </el-tag>
          </div>
          <div class="detail-row" v-if="sub.categories.length">
            <span class="label">分类：</span>
            <el-tag v-for="c in sub.categories" :key="c" size="small" type="info" class="topic-tag">
              {{ c }}
            </el-tag>
          </div>
          <div class="detail-row meta-row">
            <span>候选: {{ sub.candidateK }} 篇</span>
            <span>推送: {{ sub.topN }} 篇</span>
            <span v-if="sub.emailEnabled">📧 邮件</span>
            <span v-if="sub.feishuEnabled">💬 飞书</span>
            <span v-if="sub.autoParseFullText" class="warn-text">⚠ 自动全文解析</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑订阅' : '创建订阅'"
      width="560px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="订阅名称" required>
          <el-input v-model="form.name" placeholder="例如：Agent 论文每日推送" />
        </el-form-item>

        <el-form-item label="研究主题" required>
          <div class="tag-input-row">
            <el-input
              v-model="topicInput"
              placeholder="输入主题后按回车添加"
              @keyup.enter="addTopic"
            />
            <el-button @click="addTopic">添加</el-button>
          </div>
          <div class="tag-list">
            <el-tag
              v-for="(t, i) in form.topics"
              :key="t"
              closable
              @close="removeTopic(i)"
              class="tag-item"
            >
              {{ t }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="arXiv 分类（可选）">
          <div class="tag-input-row">
            <el-input
              v-model="categoryInput"
              placeholder="例如：cs.AI"
              @keyup.enter="addCategory"
            />
            <el-button @click="addCategory">添加</el-button>
          </div>
          <div class="tag-list">
            <el-tag
              v-for="(c, i) in form.categories"
              :key="c"
              closable
              @close="removeCategory(i)"
              type="info"
              class="tag-item"
            >
              {{ c }}
            </el-tag>
          </div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="候选数">
              <el-input-number v-model="form.candidateK" :min="5" :max="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="推送数">
              <el-input-number v-model="form.topN" :min="1" :max="10" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="Cron 表达式">
              <el-input v-model="form.cronExpr" placeholder="0 8 * * *" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="时区">
              <el-input v-model="form.timezone" placeholder="Asia/Shanghai" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider />

        <el-form-item label="推送方式">
          <el-checkbox v-model="form.emailEnabled">邮件推送</el-checkbox>
          <el-input
            v-if="form.emailEnabled"
            v-model="form.emailTo"
            placeholder="接收邮箱，多个用逗号分隔"
            style="margin-top: 8px"
          />
          <el-checkbox v-model="form.feishuEnabled" style="margin-top: 8px; display: block">
            飞书推送
          </el-checkbox>
          <el-input
            v-if="form.feishuEnabled"
            v-model="form.feishuWebhookRef"
            placeholder="飞书机器人 Webhook URL"
            style="margin-top: 8px"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.autoParseFullText">
            自动全文解析（耗时较长，默认关闭）
          </el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.subscription-view {
  max-width: 900px;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.view-header h1 {
  font-size: 24px;
  color: #e0e0e0;
  margin: 0;
}
.sub-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.sub-card {
  background-color: #1e1e1e;
  border: 1px solid #333;
  color: #e0e0e0;
}
.sub-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.sub-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.sub-info h3 {
  font-size: 16px;
  margin: 0;
  color: #e0e0e0;
}
.sub-cron {
  color: #999;
  font-size: 13px;
}
.sub-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.sub-details {
  padding-top: 8px;
  border-top: 1px solid #333;
}
.detail-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #bbb;
}
.detail-row .label {
  color: #999;
  flex-shrink: 0;
}
.topic-tag {
  font-size: 12px;
}
.meta-row {
  gap: 16px;
  color: #888;
  font-size: 12px;
}
.warn-text {
  color: #e6a23c;
}
.tag-input-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.tag-list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag-item {
  font-size: 12px;
}
</style>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useTraceStore } from '../stores/traceStore'
import { useRouter } from 'vue-router'
import TraceTimeline from '../components/trace/TraceTimeline.vue'

const traceStore = useTraceStore()
const selectedTaskType = ref('')
const selectedStatus = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)

const taskTypeOptions = [
  { value: '', label: '全部' },
  { value: 'chat', label: '聊天' },
  { value: 'paper_search', label: '论文搜索' },
  { value: 'paper_collect', label: '论文收藏' },
  { value: 'paper_parse', label: '论文解析' },
  { value: 'subscription_run', label: '订阅运行' },
]
const statusOptions = [
  { value: '', label: '全部' },
  { value: 'success', label: '成功' },
  { value: 'failed', label: '失败' },
  { value: 'running', label: '进行中' },
]

async function doQuery() {
  await traceStore.fetchTraces({
    keyword: searchKeyword.value,
    task_type: selectedTaskType.value,
    status: selectedStatus.value,
    page: currentPage.value,
  })
}

watch([selectedTaskType, selectedStatus], () => {
  currentPage.value = 1
  doQuery()
})

function handleSearch() {
  currentPage.value = 1
  doQuery()
}

async function handleViewDetail(traceId: string) {
  await traceStore.fetchTraceDetail(traceId)
}

function statusType(status: string) {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

function statusLabel(status: string) {
  switch (status) {
    case 'success': return '成功'
    case 'failed': return '失败'
    case 'running': return '进行中'
    default: return status
  }
}

onMounted(() => {
  doQuery()
})
</script>

<template>
  <div class="trace-view">
    <h1>流程查询</h1>

    <!-- Filters -->
    <div class="trace-filters">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索关键词..."
        clearable
        style="width: 240px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-select v-model="selectedTaskType" placeholder="任务类型" style="width: 140px">
        <el-option v-for="o in taskTypeOptions" :key="o.value" :label="o.label" :value="o.value" />
      </el-select>
      <el-select v-model="selectedStatus" placeholder="状态" style="width: 120px">
        <el-option v-for="o in statusOptions" :key="o.value" :label="o.label" :value="o.value" />
      </el-select>
      <el-button type="primary" @click="handleSearch">查询</el-button>
      <span class="total-count">共 {{ traceStore.total }} 条</span>
    </div>

    <!-- Trace List -->
    <div v-if="traceStore.loading" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>查询中...</p>
    </div>

    <el-empty v-else-if="traceStore.traces.length === 0" description="暂无流程记录">
      <template #image>
        <el-icon :size="60" color="#666"><List /></el-icon>
      </template>
    </el-empty>

    <div v-else class="trace-list">
      <el-card
        v-for="trace in traceStore.traces"
        :key="trace.traceId"
        class="trace-card"
        shadow="never"
        :body-style="{ padding: '16px' }"
      >
        <!-- Collapsed header -->
        <div class="trace-header" @click="handleViewDetail(trace.traceId)">
          <div class="trace-summary">
            <el-tag :type="statusType(trace.status)" size="small">
              {{ statusLabel(trace.status) }}
            </el-tag>
            <el-tag type="info" size="small">{{ trace.taskType }}</el-tag>
            <span class="trace-input">{{ trace.userInput || trace.traceId }}</span>
          </div>
          <div class="trace-meta">
            <span class="trace-duration" v-if="trace.durationMs">
              {{ (trace.durationMs / 1000).toFixed(1) }}s
            </span>
            <span class="trace-time">{{ trace.startedAt }}</span>
            <span class="trace-id-mono">{{ trace.traceId }}</span>
          </div>
        </div>

        <!-- Expanded detail -->
        <div
          v-if="traceStore.currentTrace?.traceId === trace.traceId"
          class="trace-detail"
        >
          <div class="detail-tags" v-if="trace.tags?.length">
            <el-tag
              v-for="tag in trace.tags"
              :key="tag"
              size="small"
              class="detail-tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          <div v-if="trace.errorMessage" class="detail-error">
            <strong>错误：</strong>{{ trace.errorMessage }}
          </div>
          <TraceTimeline
            :steps="traceStore.currentTrace?.steps || []"
          />
        </div>
      </el-card>

      <!-- Pagination -->
      <div v-if="traceStore.total > 20" class="pagination-row">
        <el-pagination
          v-model:current-page="currentPage"
          :total="traceStore.total"
          :page-size="20"
          layout="prev, pager, next"
          @change="doQuery"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.trace-view {
  max-width: 1000px;
}
.trace-view h1 {
  font-size: 24px;
  margin-bottom: 16px;
  color: #e0e0e0;
}
.trace-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}
.total-count {
  color: #999;
  font-size: 14px;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: #999;
}
.trace-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.trace-card {
  background-color: #1e1e1e;
  border: 1px solid #333;
  color: #e0e0e0;
}
.trace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  gap: 12px;
  flex-wrap: wrap;
}
.trace-summary {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}
.trace-input {
  font-size: 13px;
  color: #bbb;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.trace-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: #888;
  flex-shrink: 0;
}
.trace-duration {
  color: #409eff;
  font-weight: 500;
}
.trace-id-mono {
  font-family: monospace;
  font-size: 11px;
  color: #666;
}
.trace-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #333;
}
.detail-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.detail-tag {
  font-size: 11px;
}
.detail-error {
  font-size: 13px;
  color: #f56c6c;
  padding: 8px 12px;
  background-color: #2a1a1a;
  border-radius: 4px;
  margin-bottom: 8px;
}
.pagination-row {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLibraryStore } from '../stores/libraryStore'
import MarkdownViewer from '../components/common/MarkdownViewer.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const libraryStore = useLibraryStore()
const loading = ref(true)
const error = ref('')
const regenerating = ref(false)

const arxivId = route.params.arxivId as string

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    const result = await libraryStore.fetchReport(arxivId)
    if (!result.success) {
      error.value = result.message || '报告加载失败'
    }
  } catch {
    error.value = '报告加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
}

async function handleRegenerate() {
  try {
    await ElMessageBox.confirm(
      '重新生成报告将重新解析论文全文，可能需要几十秒。确定继续？',
      '重新生成',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  regenerating.value = true
  try {
    const result = await libraryStore.regenerateReport(arxivId)
    if (result.success) {
      ElMessage.success('报告已重新生成')
      await loadReport()
    } else {
      ElMessage.error(result.message || '重新生成失败')
    }
  } catch {
    ElMessage.error('重新生成请求失败')
  } finally {
    regenerating.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '确定删除该论文的解析报告？删除后可以重新生成。',
      '删除报告',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  const result = await libraryStore.deleteReport(arxivId)
  if (result.success) {
    ElMessage.success('报告已删除')
    router.back()
  } else {
    ElMessage.error(result.message || '删除失败')
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  loadReport()
})
</script>

<template>
  <div class="report-viewer">
    <div class="report-toolbar">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <span class="report-title">
        精读报告: {{ arxivId }}
      </span>
      <div class="toolbar-actions">
        <el-button
          size="small"
          :loading="regenerating"
          @click="handleRegenerate"
        >
          重新生成
        </el-button>
        <el-button
          size="small"
          type="danger"
          plain
          @click="handleDelete"
        >
          删除报告
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="report-loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载报告中...</p>
    </div>

    <div v-else-if="error" class="report-error">
      <el-empty :description="error" />
    </div>

    <div v-else class="report-content">
      <MarkdownViewer :content="libraryStore.currentReport" />
    </div>
  </div>
</template>

<style scoped>
.report-viewer {
  max-width: 900px;
  margin: 0 auto;
}
.report-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #333;
  flex-wrap: wrap;
  gap: 8px;
}
.report-title {
  color: #999;
  font-size: 14px;
  font-family: monospace;
}
.toolbar-actions {
  display: flex;
  gap: 8px;
}
.report-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: #999;
}
.report-error {
  padding: 40px;
}
.report-content {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 32px;
}
</style>

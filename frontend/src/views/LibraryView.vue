<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '../stores/libraryStore'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const libraryStore = useLibraryStore()
const searchInput = ref('')
const deleting = ref<Set<string>>(new Set())
const parsing = ref<Set<string>>(new Set())

onMounted(() => {
  libraryStore.fetchPapers()
})

function handleSearch() {
  libraryStore.setKeyword(searchInput.value)
  libraryStore.fetchPapers()
}

function handleClearSearch() {
  searchInput.value = ''
  libraryStore.setKeyword('')
  libraryStore.fetchPapers()
}

async function handleDelete(paper: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除论文 "${paper.title}" 吗？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  deleting.value.add(paper.arxivId)
  const result = await libraryStore.deletePaper(paper.arxivId)
  deleting.value.delete(paper.arxivId)

  if (result.success) {
    ElMessage.success('论文已删除')
  } else {
    ElMessage.error(result.message || '删除失败')
  }
}

async function handleParse(paper: any) {
  const arxivId = paper.arxivId
  if (parsing.value.has(arxivId)) return

  parsing.value.add(arxivId)
  try {
    const result = await libraryStore.parsePaperById(arxivId)
    if (result.success) {
      ElMessage.success({
        message: `解析完成！trace: ${result.trace_id}`,
        duration: 3000,
      })
    } else {
      ElMessage.error(result.message || '解析失败')
    }
  } catch {
    ElMessage.error('解析请求失败')
  } finally {
    parsing.value.delete(arxivId)
  }
}

function handleViewReport(paper: any) {
  router.push(`/report/${paper.arxivId}`)
}

function openArxiv(url: string) {
  window.open(url, '_blank')
}
</script>

<template>
  <div class="library-view">
    <div class="library-header">
      <h1>本地文献库</h1>
      <div class="search-bar">
        <el-input
          v-model="searchInput"
          placeholder="搜索标题或摘要..."
          clearable
          @keyup.enter="handleSearch"
          @clear="handleClearSearch"
          style="width: 320px"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <span class="total-count">{{ libraryStore.total }} 篇论文</span>
      </div>
    </div>

    <div v-if="libraryStore.loading" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <el-empty v-else-if="libraryStore.papers.length === 0" description="暂无收藏论文">
      <template #image>
        <el-icon :size="60" color="#666"><Collection /></el-icon>
      </template>
    </el-empty>

    <div v-else class="paper-list">
      <el-table
        :data="libraryStore.papers"
        stripe
        style="width: 100%"
        row-key="arxivId"
        header-row-class-name="table-header-row"
      >
        <el-table-column label="标题" min-width="280">
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="openArxiv(row.arxivUrl)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="作者" min-width="140">
          <template #default="{ row }">
            {{ row.authors?.slice(0, 3).join(', ') }}
            <template v-if="row.authors?.length > 3">等</template>
          </template>
        </el-table-column>
        <el-table-column label="日期" width="110">
          <template #default="{ row }">
            {{ row.publishedDate }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'parsed' ? 'primary' : row.status === 'collected' ? 'success' : 'info'"
              size="small"
            >
              {{ row.status === 'parsed' ? '已解析' : row.status === 'collected' ? '已收藏' : row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openArxiv(row.pdfUrl)">
              PDF
            </el-button>
            <el-button
              v-if="row.status !== 'parsed'"
              size="small"
              text
              type="success"
              :loading="parsing.has(row.arxivId)"
              @click="handleParse(row)"
            >
              解析
            </el-button>
            <el-button
              v-if="row.status === 'parsed'"
              size="small"
              text
              type="primary"
              @click="handleViewReport(row)"
            >
              查看报告
            </el-button>
            <el-button
              size="small"
              text
              type="danger"
              :loading="deleting.has(row.arxivId)"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.library-view {
  max-width: 1200px;
}
.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.library-header h1 {
  font-size: 24px;
  color: #e0e0e0;
  margin: 0;
}
.search-bar {
  display: flex;
  gap: 8px;
  align-items: center;
}
.total-count {
  color: #999;
  font-size: 14px;
  white-space: nowrap;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: #999;
}
.paper-list {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
}
.paper-list :deep(.el-table) {
  --el-table-bg-color: #1e1e1e;
  --el-table-tr-bg-color: #1e1e1e;
  --el-table-header-bg-color: #252525;
  --el-table-row-hover-bg-color: #2a2a2a;
  --el-table-border-color: #333;
  --el-table-text-color: #e0e0e0;
  --el-table-header-text-color: #aaa;
}
</style>

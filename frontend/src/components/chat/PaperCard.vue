<script setup lang="ts">
import type { PaperCardItem } from '../../types/chat'

const props = defineProps<{
  paper: PaperCardItem
}>()

const emit = defineEmits<{
  collect: [paper: PaperCardItem]
  parse: [paper: PaperCardItem]
}>()

function openPdf() {
  window.open(props.paper.pdfUrl || props.paper.arxivUrl, '_blank')
}

function openArxiv() {
  window.open(props.paper.arxivUrl, '_blank')
}
</script>

<template>
  <div class="paper-card">
    <div class="card-header">
      <h3 class="paper-title" @click="openArxiv">{{ paper.title }}</h3>
      <div class="paper-meta">
        <span v-if="paper.authors.length" class="authors">
          {{ paper.authors.slice(0, 3).join(', ') }}
          <template v-if="paper.authors.length > 3">等</template>
        </span>
        <span v-if="paper.publishedDate" class="date">{{ paper.publishedDate }}</span>
        <el-tag
          v-for="cat in paper.categories"
          :key="cat"
          size="small"
          type="info"
          class="category-tag"
        >
          {{ cat }}
        </el-tag>
      </div>
      <div class="paper-links">
        <el-link type="primary" :href="paper.arxivUrl" target="_blank" :underline="false">
          arXiv
        </el-link>
        <el-link type="primary" :href="paper.pdfUrl" target="_blank" :underline="false">
          PDF
        </el-link>
      </div>
    </div>

    <div class="card-body">
      <div class="summary-section">
        <h4>总结</h4>
        <p>{{ paper.summary }}</p>
      </div>

      <div v-if="paper.coreProblem" class="detail-section">
        <h4>核心问题</h4>
        <p>{{ paper.coreProblem }}</p>
      </div>

      <div v-if="paper.method" class="detail-section">
        <h4>方法</h4>
        <p>{{ paper.method }}</p>
      </div>

      <div v-if="paper.result" class="detail-section">
        <h4>结果</h4>
        <p>{{ paper.result }}</p>
      </div>
    </div>

    <div class="card-footer">
      <el-tag size="small" type="info">
        {{ paper.summarySource === 'abstract_intro' ? '基于摘要+引言' : '基于元数据' }}
      </el-tag>
      <div class="card-actions">
        <el-button
          v-if="paper.actions.includes('collect')"
          size="small"
          type="primary"
          plain
          @click="emit('collect', paper)"
        >
          收藏
        </el-button>
        <el-button
          v-if="paper.actions.includes('parse')"
          size="small"
          type="success"
          plain
          @click="emit('parse', paper)"
        >
          解析
        </el-button>
        <el-button
          size="small"
          @click="openPdf"
        >
          查看 PDF
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paper-card {
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}
.card-header {
  margin-bottom: 12px;
}
.paper-title {
  font-size: 16px;
  margin: 0 0 8px;
  color: #409EFF;
  cursor: pointer;
}
.paper-title:hover {
  text-decoration: underline;
}
.paper-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  color: #999;
  font-size: 13px;
}
.paper-links {
  display: flex;
  gap: 16px;
}
.category-tag {
  font-size: 11px;
}
.card-body h4 {
  font-size: 13px;
  color: #bbb;
  margin: 8px 0 4px;
}
.card-body p {
  font-size: 13px;
  color: #ccc;
  line-height: 1.6;
  margin: 0;
}
.detail-section {
  margin-top: 4px;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #333;
}
.card-actions {
  display: flex;
  gap: 8px;
}
</style>

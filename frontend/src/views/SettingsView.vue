<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '../stores/settingsStore'
import { ElMessage } from 'element-plus'

const store = useSettingsStore()

const form = ref({
  defaultCandidateK: 20,
  defaultTopN: 2,
  preferredCategories: '',
  preferredTopics: '',
  summaryLanguage: 'zh-CN',
  autoParseFullText: false,
})

onMounted(async () => {
  await store.fetchPreferences()
  form.value.defaultCandidateK = store.getInt('default_candidate_k', 20)
  form.value.defaultTopN = store.getInt('default_top_n', 2)
  form.value.preferredCategories = store.preferences.preferred_categories || ''
  form.value.preferredTopics = store.preferences.preferred_topics || ''
  form.value.autoParseFullText = store.getBool('auto_parse_full_text')
})

async function handleSave() {
  const result = await store.savePreferences({
    default_candidate_k: form.value.defaultCandidateK,
    default_top_n: form.value.defaultTopN,
    preferred_categories: form.value.preferredCategories,
    preferred_topics: form.value.preferredTopics,
    auto_parse_full_text: form.value.autoParseFullText,
  })
  if (result?.success) {
    ElMessage.success('设置已保存')
  } else {
    ElMessage.error(result?.message || '保存失败')
  }
}
</script>

<template>
  <div class="settings-view">
    <h1>设置</h1>

    <div class="settings-section">
      <h2>搜索默认值</h2>
      <el-form label-position="top" class="settings-form">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="候选池大小 (Candidate K)">
              <el-input-number
                v-model="form.defaultCandidateK"
                :min="5"
                :max="100"
              />
              <div class="form-hint">arXiv 每次搜索返回的候选论文数量</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认返回数量 (Top N)">
              <el-input-number
                v-model="form.defaultTopN"
                :min="1"
                :max="20"
              />
              <div class="form-hint">筛选后展示给用户的论文数量</div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <div class="settings-section">
      <h2>偏好设置</h2>
      <el-form label-position="top" class="settings-form">
        <el-form-item label="偏好分类">
          <el-input
            v-model="form.preferredCategories"
            placeholder="例如：cs.AI, cs.CL, stat.ML（逗号分隔）"
          />
          <div class="form-hint">设置后搜索结果会偏向这些分类</div>
        </el-form-item>

        <el-form-item label="偏好主题">
          <el-input
            v-model="form.preferredTopics"
            placeholder="例如：reinforcement learning, LLM（逗号分隔）"
          />
          <div class="form-hint">订阅任务默认主题关键词</div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.autoParseFullText">
            订阅任务默认自动全文解析
          </el-checkbox>
          <div class="form-hint">开启后订阅推送的论文会自动解析，耗时较长</div>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h2>AI 配置</h2>
      <el-descriptions :column="1" border class="config-table">
        <el-descriptions-item label="LLM Provider">
          <el-tag size="small" :type="store.preferences.llmAvailable ? 'success' : 'info'">
            {{ store.preferences.llmProvider || 'openai' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="LLM 模型">
          {{ store.preferences.llmModel || '未配置' }}
        </el-descriptions-item>
        <el-descriptions-item label="API Key">
          <span :style="{ color: store.preferences.llmApiKeySet ? '#67c23a' : '#f56c6c' }">
            {{ store.preferences.llmApiKeySet ? '已配置' : '未配置' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag size="small" :type="store.preferences.llmAvailable ? 'success' : 'warning'">
            {{ store.preferences.llmAvailable ? 'LLM 增强可用' : '降级到规则模式' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <p class="config-note">
        LLM 配置在 backend/.env 中修改：<br/>
        <code>LLM_PROVIDER</code>（openai/deepseek/qwen/openai-compatible）<br/>
        <code>LLM_API_KEY</code>、<code>LLM_MODEL</code>
      </p>
    </div>

    <div class="save-bar">
      <el-button
        type="primary"
        size="large"
        :loading="store.saving"
        @click="handleSave"
      >
        保存设置
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 700px;
}
.settings-view h1 {
  font-size: 24px;
  margin-bottom: 24px;
  color: #e0e0e0;
}
.settings-section {
  margin-bottom: 32px;
}
.settings-section h2 {
  font-size: 16px;
  color: #ccc;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #333;
}
.settings-form {
  max-width: 600px;
}
.form-hint {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}
.config-table {
  background-color: #1e1e1e;
}
.config-note {
  margin-top: 12px;
  font-size: 13px;
  color: #888;
  line-height: 1.6;
}
.config-note code {
  background-color: #2a2a2a;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}
.save-bar {
  padding-top: 16px;
  border-top: 1px solid #333;
}
</style>

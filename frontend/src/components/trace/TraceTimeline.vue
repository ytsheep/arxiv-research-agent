<script setup lang="ts">
import type { TraceStep } from '../../types/trace'

const props = defineProps<{
  steps: TraceStep[]
}>()

function stepIcon(status: string): string {
  switch (status) {
    case 'success': return 'Check'
    case 'failed': return 'Close'
    case 'skipped': return 'Remove'
    default: return 'More'
  }
}

function stepColor(status: string): string {
  switch (status) {
    case 'success': return '#67c23a'
    case 'failed': return '#f56c6c'
    case 'skipped': return '#909399'
    default: return '#409eff'
  }
}
</script>

<template>
  <div v-if="steps.length > 0" class="trace-timeline">
    <div class="timeline-title">执行步骤</div>
    <div class="steps-list">
      <div
        v-for="(step, idx) in steps"
        :key="idx"
        class="step-item"
        :class="{ 'is-last': idx === steps.length - 1 }"
      >
        <div class="step-line">
          <div class="step-dot" :style="{ borderColor: stepColor(step.status) }">
            <el-icon :size="12" :color="stepColor(step.status)">
              <component :is="stepIcon(step.status)" />
            </el-icon>
          </div>
          <div v-if="idx < steps.length - 1" class="step-connector" />
        </div>
        <div class="step-content">
          <div class="step-header">
            <span class="step-name">{{ step.stepName }}</span>
            <el-tag
              :type="step.status === 'success' ? 'success' : step.status === 'failed' ? 'danger' : 'info'"
              :disable-transitions="true"
              size="small"
            >
              {{ step.status === 'success' ? '成功' : step.status === 'failed' ? '失败' : step.status }}
            </el-tag>
          </div>
          <div v-if="step.toolName && step.toolName !== step.stepName" class="step-action">
            <span class="info-label">Action：</span>
            <el-tag size="small" type="warning" :disable-transitions="true">{{ step.toolName }}</el-tag>
          </div>
          <div v-if="step.reasoningSummary" class="step-reasoning">
            <el-icon :size="14"><component :is="'More'" /></el-icon>
            <span>{{ step.reasoningSummary }}</span>
          </div>
          <div v-if="step.inputSummary" class="step-info">
            <span class="info-label">输入：</span>{{ step.inputSummary }}
          </div>
          <div v-if="step.outputSummary" class="step-info">
            <span class="info-label">输出：</span>{{ step.outputSummary }}
          </div>
          <div v-if="step.errorMessage" class="step-error">
            <el-icon :size="14"><WarningFilled /></el-icon>
            {{ step.errorMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="no-steps">
    暂无步骤详情
  </div>
</template>

<style scoped>
.trace-timeline {
  margin-top: 16px;
}
.timeline-title {
  font-size: 14px;
  font-weight: 600;
  color: #bbb;
  margin-bottom: 12px;
}
.steps-list {
  display: flex;
  flex-direction: column;
}
.step-item {
  display: flex;
  gap: 12px;
  min-height: 48px;
}
.step-item.is-last {
  min-height: auto;
}
.step-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
  flex-shrink: 0;
}
.step-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #999;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1e1e1e;
  flex-shrink: 0;
}
.step-connector {
  width: 2px;
  flex: 1;
  background-color: #444;
  margin: 4px 0;
}
.step-content {
  flex: 1;
  padding-bottom: 16px;
}
.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.step-name {
  font-size: 13px;
  color: #ddd;
  font-weight: 500;
}
.step-action {
  font-size: 12px;
  color: #e6a23c;
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.step-reasoning {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
  padding: 4px 8px;
  background: rgba(103, 194, 58, 0.08);
  border-radius: 4px;
  border-left: 2px solid #67c23a;
}
.step-info {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
  word-break: break-all;
}
.info-label {
  color: #777;
}
.step-error {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
}
.no-steps {
  color: #888;
  font-size: 13px;
  text-align: center;
  padding: 20px;
}
</style>

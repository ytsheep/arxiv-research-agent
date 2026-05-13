<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', label: '聊天', icon: 'ChatDotRound' },
  { path: '/library', label: '本地文献库', icon: 'Collection' },
  { path: '/subscriptions', label: '订阅任务', icon: 'Bell' },
  { path: '/traces', label: '流程查询', icon: 'List' },
  { path: '/settings', label: '设置', icon: 'Setting' },
]
</script>

<template>
  <el-menu
    :default-active="route.path"
    router
    class="side-nav"
    background-color="#1f1f1f"
    text-color="#999"
    active-text-color="#409EFF"
  >
    <div class="nav-header">
      <h2>arXiv Agent</h2>
    </div>
    <el-menu-item
      v-for="item in navItems"
      :key="item.path"
      :index="item.path"
    >
      <el-icon><component :is="item.icon" /></el-icon>
      <span>{{ item.label }}</span>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
.side-nav {
  height: 100%;
  border-right: none;
}
.nav-header {
  padding: 20px 16px 12px;
  text-align: center;
}
.nav-header h2 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}
</style>

<script setup lang="ts">
import SideNav from './SideNav.vue'
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <SideNav />
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background-color: #141414;
  color: #e0e0e0;
}
.sidebar {
  width: 220px;
  flex-shrink: 0;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>

<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from "vue-router";
</script>

<style scoped>
body {
  padding-top: 60px; /* 添加顶部内边距，避免内容被 header 遮挡 */
  margin: 0;
  overflow-x: hidden; /* 防止水平滚动条 */
}
</style>

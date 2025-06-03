<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from "vue-router";
</script>

<style>
/* 全局样式设置 */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100%;
}
</style>

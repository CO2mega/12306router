<template>
  <div class="app-container">
    <Header />
    <div class="main-content-wrapper">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import Header from "@/components/header.vue";
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.main-content-wrapper {
  margin-top: 60px; /* Header的高度，确保内容不被header覆盖 */
  flex: 1;
  width: 100%;
}
</style>
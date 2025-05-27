<template>
  <div class="header-container">
    <div class="header-left flex-box">
      <span class="logo">12306</span>
      <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        mode="horizontal"
        background-color="#1976d2"
        text-color="#fff"
        active-text-color="#ffd04b"
        :ellipsis="false"
        @select="handleSelect"
      >
        <el-menu-item index="1">首页</el-menu-item>
        <el-sub-menu index="2">
          <template #title>车票</template>
          <el-menu-item index="2-1">车票</el-menu-item>
          <el-menu-item index="2-2">常用查询</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </div>
    <div class="header-right">
      <el-button type="primary" size="small" @click="goLogin">登录</el-button>
      <el-button type="text" size="small" @click="goRegister">注册</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { ref } from "vue";
const route = useRoute();
const router = useRouter();

const activeIndex = ref("1");
const handleSelect = (key) => {
  if (key === "1") router.push("/");
  if (key === "2-1") router.push("/ticket");
  if (key === "2-2") router.push("/query");
};

const goLogin = () => {
  router.push("/login");
};
const gosignup = () => {
  router.push("/signup");
};
</script>

<style scoped>
.header-container {
  width: 100vw;
  height: 64px;
  background: #1976d2;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  padding: 0 40px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo {
  font-size: 28px;
  font-weight: bold;
  margin-right: 32px;
  letter-spacing: 2px;
}

.el-menu-demo {
  background: transparent;
  border-bottom: none;
  color: #fff;
  min-width: 400px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.el-button--primary {
  background: #fff;
  color: #1976d2;
  border: none;
}

.el-button--text {
  color: #fff;
}
</style>

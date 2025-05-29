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
          <template #default>
            <div class="submenu-columns">
              <div class="submenu-col">
                <div class="submenu-title active">购买</div>
                <div class="submenu-item">单程</div>
                <div class="submenu-item">中转换乘</div>
              </div>
              <div class="submenu-col">
                <div class="submenu-title"></div>
                <div class="submenu-item">往返</div>
                <div class="submenu-item">计次·定期票</div>
              </div>
              <div class="submenu-col">
                <div class="submenu-title active">变更</div>
                <div class="submenu-item">退票</div>
                <div class="submenu-item">变更到站</div>
              </div>
              <div class="submenu-col">
                <div class="submenu-title"></div>
                <div class="submenu-item">改签</div>
              </div>
            </div>
          </template>
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

.submenu-columns {
  display: flex;
  min-width: 520px;
  padding: 18px 0 18px 0;
  background: #fff;
  color: #333;
  box-shadow: 0 2px 8px rgba(32, 94, 201, 0.08);
  border-radius: 6px;
  gap: 32px;
  border: none;
}
.submenu-col {
  display: flex;
  flex-direction: column;
  min-width: 100px;
  border-right: 1px solid #e3eefd;
  padding: 0 24px;
}
.submenu-col:last-child {
  border-right: none;
}
.submenu-title {
  font-weight: 500;
  color: #1976d2;
  margin-bottom: 8px;
  font-size: 16px;
}
.submenu-title.active {
  color: #1976d2;
}
.submenu-item {
  color: #333;
  font-size: 15px;
  padding: 6px 0;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}
.submenu-item:hover {
  background: #f5f7fa;
  color: #1976d2;
}
</style>

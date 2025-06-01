<template>
  <div class="header">
    <div class="logo" @click="goToHome">
      <span class="logo-text">12306</span>
    </div>
    <div class="nav-menu">
      <router-link to="/ticket" class="nav-item">车票</router-link>
      <router-link to="/change-ticket" class="nav-item">改签</router-link>
    </div>
    <div class="nav-links">
      <template v-if="userInfo">
        <div class="user-info" @click="goToUserProfile">
          <span class="username">{{ userInfo.account }}</span>
        </div>
      </template>
      <template v-else>
        <router-link to="/login">登录</router-link>
        <router-link to="/register">注册</router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userInfo = ref(null);

// 获取用户信息
onMounted(() => {
  const savedUser = localStorage.getItem('user');
  if (savedUser) {
    userInfo.value = JSON.parse(savedUser);
  }
});

// 跳转到用户信息页面
const goToUserProfile = () => {
  router.push('/user-profile');
};

// 添加返回首页方法
const goToHome = () => {
  router.push('/');
};
</script>

<style scoped>
.header {
  position: fixed;  /* 固定在顶部 */
  top: 0;
  left: 0;
  right: 0;
  width: 100vw;  /* 使用视口宽度 */
  height: 60px;
  background-color: #205ec9;
  display: flex;
  justify-content: flex-start;  /* 改为左对齐 */
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
  z-index: 1000;  /* 确保header始终在最上层 */
}

/* 为了防止内容被fixed header遮挡，需要给body添加padding-top */
:deep(body) {
  padding-top: 60px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer; /* 添加手型光标 */
  transition: opacity 0.3s; /* 添加过渡效果 */
}

.logo:hover {
  opacity: 0.8; /* 添加悬停效果 */
}

.logo-text {
  color: white;
  font-size: 24px;
  font-weight: bold;
  letter-spacing: 2px;
}

.nav-menu {
  display: flex;
  gap: 30px;
  margin-left: 40px;
}

.nav-item {
  color: white;
  text-decoration: none;
  font-size: 16px;
  padding: 5px 15px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: #174a9c;
}

.nav-item.router-link-active {
  background-color: #174a9c;
}

.nav-links {
  margin-left: auto;  /* 将用户相关链接推到最右边 */
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-size: 16px;
}

.nav-links a:hover {
  opacity: 0.8;
}

.user-info {
  cursor: pointer;
  color: white;
  padding: 5px 15px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #174a9c;
}

.username {
  font-size: 16px;
  font-weight: 500;
}
</style>

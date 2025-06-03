<template>
  <div class="header">
    <div class="left-section">
      <div class="logo" @click="goToHome">
        <span class="logo-text">12306</span>
      </div>
      <div class="nav-menu">
        <router-link to="/ticket" class="nav-item">车票</router-link>
        <router-link to="/change-ticket" class="nav-item">改退</router-link>
      </div>
    </div>
    <div class="nav-links">
      <template v-if="userInfo">
        <div class="user-info" @click="toggleDropdown">
          <span class="username">{{ userInfo.account }}</span>
          <div class="dropdown-menu" v-if="showDropdown">
            <div class="dropdown-item" @click="goToUserProfile">个人中心</div>
            <div class="dropdown-item" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </template>
      <template v-else>
        <router-link to="/login" class="auth-link">登录</router-link>
        <router-link to="/register" class="auth-link">注册</router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userInfo = ref(null);
const showDropdown = ref(false);

// 获取用户信息，并添加调试信息
function getUserInfo() {
  try {
    console.log('尝试获取用户信息...');
    const userJson = localStorage.getItem('user');
    console.log('localStorage中的user:', userJson);
    
    if (userJson) {
      const parsedUser = JSON.parse(userJson);
      console.log('解析后的用户信息:', parsedUser);
      userInfo.value = parsedUser;
    } else {
      console.log('未找到用户信息');
      userInfo.value = null;
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    userInfo.value = null;
  }
}

// 添加一个刷新用户状态的函数，可以手动调用
function refreshUserStatus() {
  getUserInfo();
}

// 跳转到首页
function goToHome() {
  router.push('/');
}

// 跳转到用户个人中心
function goToUserProfile() {
  router.push('/user-profile');
  showDropdown.value = false; // 关闭下拉菜单
}

// 退出登录
function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('userId');
  userInfo.value = null;
  showDropdown.value = false;
  ElMessage.success('已退出登录');
  router.push('/');
}

// 切换下拉菜单
function toggleDropdown() {
  showDropdown.value = !showDropdown.value;
}

// 点击外部时关闭下拉菜单
function closeDropdown(e) {
  const userInfoEl = document.querySelector('.user-info');
  if (userInfoEl && !userInfoEl.contains(e.target)) {
    showDropdown.value = false;
  }
}

// 组件挂载时获取用户信息和添加点击事件监听器
onMounted(() => {
  console.log('Header组件挂载');
  getUserInfo();
  document.addEventListener('click', closeDropdown);
  
  // 监听存储变化，实时更新用户状态
  window.addEventListener('storage', getUserInfo);
  
  // 每次路由变化时重新获取用户信息
  router.afterEach(() => {
    console.log('路由变化，重新获取用户信息');
    getUserInfo();
  });
  
  // 定期检查用户状态（每5秒）
  const interval = setInterval(getUserInfo, 5000);
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(interval);
    document.removeEventListener('click', closeDropdown);
    window.removeEventListener('storage', getUserInfo);
  });
});

// 组件卸载时移除事件监听器
onUnmounted(() => {
  document.removeEventListener('click', closeDropdown);
  window.removeEventListener('storage', getUserInfo);
});
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  height: 60px;
  background-color: #205ec9;
  display: flex;
  justify-content: space-between; /* 两端对齐 */
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.left-section {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 25px; /* Logo与导航菜单间距 */
}

.logo-text {
  font-size: 22px;
  font-weight: bold;
  color: #fff;
}

.nav-menu {
  display: flex;
  gap: 24px;
}

.nav-item {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 16px;
  padding: 5px 15px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-item:hover, .nav-item.router-link-active {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.15);
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #fff;
}

.user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.username {
  color: #fff;
  font-size: 15px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  min-width: 120px;
  margin-top: 8px;
  z-index: 1001;
}

.dropdown-item {
  padding: 10px 15px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f5f7fa;
  color: #205ec9;
}

.dropdown-item:first-child {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.dropdown-item:last-child {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}

.auth-link {
  color: white !important;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.auth-link:hover {
  background-color: rgba(255, 255, 255, 0.15);
}
</style>

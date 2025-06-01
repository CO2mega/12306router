<template>
  <div class="user-profile">
    <Header />
    <div class="profile-container">
      <h2>用户信息</h2>
      <div class="profile-content" v-if="userInfo">
        <div class="info-item">
          <label>用户账号：</label>
          <span>{{ userInfo.account }}</span>
        </div>
        <!-- 可以添加更多用户信息字段 -->
        <div class="actions">
          <button @click="logout">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Header from '@/components/header.vue';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userInfo = ref(null);

onMounted(() => {
  const savedUser = localStorage.getItem('user');
  if (savedUser) {
    userInfo.value = JSON.parse(savedUser);
  } else {
    router.push('/login');
  }
});

const logout = () => {
  localStorage.removeItem('user');
  router.push('/login');
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  background: #f7faff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 80, 180, 0.08);
}

h2 {
  color: #205ec9;
  margin-bottom: 30px;
}

.profile-content {
  padding: 20px;
}

.info-item {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.info-item label {
  width: 100px;
  color: #666;
}

.actions {
  margin-top: 30px;
  text-align: center;
}

button {
  padding: 8px 24px;
  background: #205ec9;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #174a9c;
}
</style>
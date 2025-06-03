<template>
  <div class="login-container">
    <h2>用户登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="account">账户名</label>
        <input id="account" v-model="account" type="text" placeholder="请输入账户名" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input id="password" v-model="password" type="password" placeholder="请输入密码" required />
      </div>
      <div class="form-options">
        <label class="remember-me">
          <input type="checkbox" v-model="rememberMe" />
          <span>记住我</span>
        </label>
        <a class="forgot-password" @click="showReset = true">忘记密码?</a>
      </div>
      <div class="form-actions">
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <button type="button" class="register-btn" @click="goToRegister">注册账户</button>
      </div>
    </form>

    <!-- 重置密码对话框 - 修改为直接重置密码的版本 -->
    <div v-if="showReset" class="reset-modal">
      <div class="reset-content">
        <h3>重置密码</h3>
        <div class="form-group">
          <label for="reset-account">账户名</label>
          <input id="reset-account" v-model="resetAccount" type="text" placeholder="请输入账户名" />
        </div>
        <div class="form-group">
          <label for="new-password">新密码</label>
          <input id="new-password" v-model="newPassword" type="password" placeholder="请输入新密码" />
        </div>
        <div class="form-group">
          <label for="confirm-password">确认密码</label>
          <input id="confirm-password" v-model="confirmPassword" type="password" placeholder="请再次输入新密码" />
        </div>
        <div class="reset-actions">
          <button @click="submitReset" :disabled="resetLoading">
            {{ resetLoading ? '提交中...' : '提交' }}
          </button>
          <button @click="cancelReset">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import request from '@/utils/request';
import { ElMessage } from 'element-plus';

const account = ref("");
const password = ref("");
const rememberMe = ref(false);
const showReset = ref(false);
const resetAccount = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const resetLoading = ref(false);
const router = useRouter();

// 检查是否有记住的登录信息
onMounted(() => {
  const savedAccount = localStorage.getItem('savedAccount');
  if (savedAccount) {
    account.value = savedAccount;
    rememberMe.value = true;
  }
});

// 处理登录
async function handleLogin() {
  if (!account.value || !password.value) {
    ElMessage.warning('请输入账户和密码');
    return;
  }

  loading.value = true;
  
  try {
    const res = await request.post("/api/login", {
      account: account.value,
      password: password.value
    });
    
    console.log('登录响应：', res.data);
    
    if (res.data.code === 0) {
      // 记住用户名
      if (rememberMe.value) {
        localStorage.setItem('savedAccount', account.value);
      } else {
        localStorage.removeItem('savedAccount');
      }
      
      // 存储用户信息
      localStorage.setItem('token', res.data.data.token);
      
      const userData = {
        id: res.data.data.user.id,
        account: res.data.data.user.account
      };
      console.log('存储的用户数据：', userData);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('userId', userData.id);
      
      ElMessage.success('登录成功');
      
      // 强制触发storage事件
      window.dispatchEvent(new Event('storage'));
      
      router.push('/');
    } else {
      ElMessage.error(res.data.msg || '账户或密码错误');
    }
  } catch (error) {
    console.error('登录错误：', error);
    ElMessage.error('网络错误，请稍后重试');
  } finally {
    loading.value = false;
  }
}

// 提交重置密码请求 - 修改为直接重置密码
async function submitReset() {
  // 验证输入
  if (!resetAccount.value) {
    ElMessage.warning('请输入账户名');
    return;
  }
  
  if (!newPassword.value || !confirmPassword.value) {
    ElMessage.warning('请输入新密码和确认密码');
    return;
  }
  
  if (newPassword.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  
  resetLoading.value = true;
  
  try {
    const res = await request.post("/api/reset-password", {
      account: resetAccount.value,
      newPassword: newPassword.value,
      confirmPassword: confirmPassword.value
    });
    
    if (res.data.code === 0) {
      ElMessage.success('密码重置成功，请使用新密码登录');
      cancelReset();
    } else {
      ElMessage.error(res.data.msg || '重置密码失败');
    }
  } catch (error) {
    console.error('重置密码错误：', error);
    ElMessage.error('网络错误，请稍后重试');
  } finally {
    resetLoading.value = false;
  }
}

// 取消重置密码并清空表单
function cancelReset() {
  showReset.value = false;
  resetAccount.value = "";
  newPassword.value = "";
  confirmPassword.value = "";
}

// 跳转到注册页面
function goToRegister() {
  router.push('/register');
}
</script>

<style scoped>
/* 登录页样式 */
.login-container {
  max-width: 400px;
  margin: 60px auto;
  padding: 30px;
  background: #f9fbff;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

h2 {
  text-align: center;
  color: #205ec9;
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 15px;
  transition: border 0.3s;
}

.form-group input:focus {
  border-color: #205ec9;
  outline: none;
}

.form-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.forgot-password {
  color: #205ec9;
  text-decoration: none;
  cursor: pointer;
}

.forgot-password:hover {
  text-decoration: underline;
}

.form-actions {
  display: flex;
  gap: 15px;
}

.login-btn, .register-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn {
  background: #205ec9;
  color: white;
}

.login-btn:hover {
  background: #1a4da3;
}

.register-btn {
  background: #f0f2f5;
  color: #205ec9;
  border: 1px solid #ddd;
}

.register-btn:hover {
  background: #e0e5eb;
}

.login-btn:disabled {
  background: #95b7e8;
  cursor: not-allowed;
}

/* 重置密码弹窗样式 */
.reset-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.reset-content {
  width: 90%;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  padding: 25px;
}

.reset-content h3 {
  margin-top: 0;
  color: #205ec9;
}

.reset-content .form-group {
  margin-bottom: 15px;
}

.reset-content label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
}

.reset-content input {
  width: 100%;
  padding: 10px;
  margin: 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.reset-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.reset-actions button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.reset-actions button:first-child {
  background: #205ec9;
  color: white;
}

.reset-actions button:first-child:disabled {
  background: #95b7e8;
  cursor: not-allowed;
}

.reset-actions button:last-child {
  background: #f0f2f5;
  color: #333;
}
</style>
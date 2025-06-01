<template>
    <div>
        <Header />
        <div class="login-container">
            <h2>登录</h2>
            <form @submit.prevent="handleLogin">
                <div class="form-group">
                    <label for="account">账户</label>
                    <input id="account" v-model="account" type="text" required placeholder="请输入账户" />
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input id="password" v-model="password" type="password" required placeholder="请输入密码" />
                </div>
                <!-- 添加记住密码选项 -->
                <div class="remember-me">
                    <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
                </div>
                <div class="form-actions">
                    <button type="submit">登录</button>
                    <button type="button" @click="resetPassword">重置密码</button>
                </div>
            </form>
            <div v-if="showReset" class="reset-password">
                <h3>重置密码</h3>
                <input v-model="resetAccount" type="text" placeholder="请输入账户" />
                <button @click="submitReset">提交</button>
                <button @click="showReset = false">取消</button>
                <div style="margin-top: 18px; text-align: right;">
                    <button @click="registerAccount" type="button">注册账号</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Header from "@/components/header.vue";
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import request from '@/utils/request';

const account = ref("");
const password = ref("");
const showReset = ref(false);
const resetAccount = ref("");
const rememberMe = ref(localStorage.getItem('rememberMe') === 'true');
const router = useRouter();

// 在组件挂载时检查是否有保存的账号密码
onMounted(() => {
    const token = localStorage.getItem("token");
    if (token) {
        router.push("/");
        return;
    }

    // 如果之前选择了记住密码，则自动填充
    if (localStorage.getItem('rememberMe') === 'true') {
        const savedAccount = localStorage.getItem('savedAccount');
        const savedPassword = localStorage.getItem('savedPassword');
        if (savedAccount && savedPassword) {
            account.value = savedAccount;
            password.value = atob(savedPassword); // 解码保存的密码
        }
    }
});

async function handleLogin() {
    try {
        const res = await request.post("/api/login", {
            account: account.value,
            password: password.value
        });

        if (res.data.code === 0) {
            // 保存登录状态
            localStorage.setItem("token", res.data.data.token);
            localStorage.setItem("user", JSON.stringify(res.data.data.user));
            
            // 处理记住密码
            localStorage.setItem('rememberMe', rememberMe.value);
            if (rememberMe.value) {
                localStorage.setItem('savedAccount', account.value);
                localStorage.setItem('savedPassword', btoa(password.value)); // 使用base64编码存储密码
            } else {
                // 如果取消记住密码，则清除保存的信息
                localStorage.removeItem('savedAccount');
                localStorage.removeItem('savedPassword');
            }

            ElMessage.success("登录成功！");
            router.push("/"); 
        } else {
            ElMessage.error(res.data.msg || "登录失败");
        }
    } catch (error) {
        console.error("登录错误:", error);
        ElMessage.error("网络错误，请稍后重试");
    }
}

function resetPassword() {
    showReset.value = true;
}

async function submitReset() {
    try {
        const res = await axios.post("http://localhost:3000/api/reset-password", {
            account: resetAccount.value
        });

        if (res.data.code === 0) {
            alert("重置密码邮件已发送，请查收");
        } else {
            alert(res.data.msg || "重置密码失败");
        }
    } catch (error) {
        console.error("重置密码错误:", error);
        alert("网络错误，请稍后重试");
    }
    showReset.value = false;
    resetAccount.value = "";
}

function registerAccount() {
    router.push("/register");
}

// 检查是否已登录
onMounted(() => {
    const token = localStorage.getItem("token");
    if (token) {
        router.push("/");
    }
});
</script>

<style scoped>
body, html, #app {
    height: 100%;
    margin: 0;
    padding: 0;
}
  
/* 新增外层居中样式 */
:deep(body) {
    min-height: 100vh;
    margin: 0;
    padding: 0;
}
  
/* 让父容器居中 */
.login-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    max-width: 480px;
    min-height: 480px;
    margin: 0 auto;
    padding: 36px 28px;
    border-radius: 12px;
    background: #f7faff;
    box-shadow: 0 4px 24px rgba(0, 80, 180, 0.08);
    border: 1px solid #e3eefd;
    /* 让容器在父级中垂直居中 */
    position: relative;
    top: 50vh;
    transform: translateY(-50%);
}

.login-header {
    width: 100vw;
    background: #205ec9;
    padding: 0 0 0 32px;
    height: 56px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 8px rgba(32, 94, 201, 0.08);
}

.header-title {
    display: flex;
    align-items: center;
    font-size: 20px;
    color: #fff;
    font-weight: bold;
    letter-spacing: 2px;
}

.logo {
    height: 32px;
    margin-right: 12px;
}

h2 {
    color: #205ec9;
    text-align: center;
    margin-bottom: 28px;
    letter-spacing: 2px;
}

.form-group {
    margin-bottom: 22px;
}

.form-group label {
    display: block;
    margin-bottom: 7px;
    color: #205ec9;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #b7d0f7;
    border-radius: 5px;
    background: #fff;
    font-size: 15px;
    transition: border 0.2s;
}

.form-group input:focus {
    border: 1.5px solid #205ec9;
    outline: none;
}

.captcha-group {
    display: flex;
    align-items: center;
}

.captcha-input {
    width: auto;
    min-width: 30px;
    max-width: 80px;
    margin-left: 10px;
    margin-right: 12px;
    padding: 8px 6px;
    /* 保证和其他输入框高度一致 */
    box-sizing: border-box;
}

.captcha-img {
    height: 36px;
    width: auto;
    cursor: pointer;
    border: 1px solid #b7d0f7;
    border-radius: 5px;
    background: #fff;
    transition: box-shadow 0.2s;
}

.captcha-img:hover {
    box-shadow: 0 0 4px #205ec9;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 18px;
}

.form-actions button {
    padding: 7px 22px;
    border: none;
    border-radius: 5px;
    background: #205ec9;
    color: #fff;
    font-weight: 500;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s;
}

.form-actions button[type="button"] {
    background: #e3eefd;
    color: #205ec9;
}

.form-actions button:hover {
    background: #174a9c;
}

.form-actions button[type="button"]:hover {
    background: #c6dafc;
}

.reset-password {
    margin-top: 24px;
    padding: 18px;
    border: 1px solid #b7d0f7;
    border-radius: 8px;
    background: #eaf2fd;
}

.reset-password h3 {
    color: #205ec9;
    margin-bottom: 12px;
}

.reset-password input {
    width: 68%;
    margin-right: 10px;
    padding: 7px 10px;
    border: 1px solid #b7d0f7;
    border-radius: 5px;
    background: #fff;
}

.reset-password button {
    padding: 6px 16px;
    border: none;
    border-radius: 5px;
    background: #205ec9;
    color: #fff;
    font-size: 14px;
    margin-right: 6px;
    cursor: pointer;
    transition: background 0.2s;
}

.reset-password button:last-child {
    background: #e3eefd;
    color: #205ec9;
}

.reset-password button:hover:not(:last-child) {
    background: #174a9c;
}

.reset-password button:last-child:hover {
    background: #c6dafc;
}

/* 添加记住密码选项的样式 */
.remember-me {
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    color: #205ec9;
}

.remember-me :deep(.el-checkbox__label) {
    color: #205ec9;
}

.remember-me :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: #205ec9;
    border-color: #205ec9;
}
</style>
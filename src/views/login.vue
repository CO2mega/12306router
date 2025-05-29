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
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const account = ref("");
const password = ref("");
const user = ref(null); // Store user state globally
const router = useRouter();

function handleLogin() {
    axios.post("http://localhost:3000/api/login", {
        account: account.value,
        password: password.value
    })
    .then(res => {
        if (res.data.code === 0) {
            user.value = res.data.user; // Save user data
            localStorage.setItem("user", JSON.stringify(res.data.user));
            alert("登录成功！");
            router.push("/"); // Redirect to homepage
        } else {
            alert(res.data.msg || "登录失败");
        }
    })
    .catch(() => {
        alert("网络错误，请稍后重试");
    });
}
function resetPassword() {
    showReset.value = true;
}
function submitReset() {
    alert(`重置密码账户：${resetAccount.value}`);
    showReset.value = false;
    resetAccount.value = "";
}
function registerAccount() {
    alert("跳转到注册账号页面或弹出注册表单");
}
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
</style>
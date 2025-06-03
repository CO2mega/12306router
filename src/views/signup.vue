<template>
    <div>
        <Header />
        <div class="signup-container">
            <h2>注册账号</h2>
            <form @submit.prevent="handleSignup">
                <div class="form-group">
                    <label for="account">账户</label>
                    <input id="account" v-model="account" type="text" required placeholder="请输入账户名" />
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input id="password" v-model="password" type="password" required placeholder="请输入密码" />
                </div>
                <div class="form-group">
                    <label for="confirm-password">确认密码</label>
                    <input id="confirm-password" v-model="confirmPassword" type="password" required placeholder="请再次输入密码" />
                </div>
                <div class="form-group captcha-group">
                    <label for="captcha">验证码</label>
                    <input id="captcha" v-model="captcha" class="captcha-input" type="text" required placeholder="验证码" />
                    <img @click="refreshCaptcha" :src="captchaUrl" alt="验证码" class="captcha-img" />
                </div>
                <div class="form-actions">
                    <button type="submit">注册</button>
                    <button type="button" @click="goToLogin">返回登录</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import Header from "@/components/header.vue";
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import request from '@/utils/request';
import { ElMessage } from 'element-plus';

const router = useRouter();
const account = ref("");
const password = ref("");
const confirmPassword = ref("");
const captcha = ref("");
const captchaUrl = ref("http://localhost:3000/api/captcha?" + Math.random());

// 刷新验证码
function refreshCaptcha() {
    captchaUrl.value = "http://localhost:3000/api/captcha?" + Math.random();
}

// 注册处理函数
async function handleSignup() {
    // 表单验证
    if (password.value !== confirmPassword.value) {
        ElMessage.error("两次密码输入不一致");
        return;
    }

    try {
        const res = await request.post("/api/register", {
            account: account.value,
            password: password.value,
            captcha: captcha.value
        });

        if (res.data.code === 0) {
            ElMessage.success("注册成功，请登录!");
            router.push("/login");
        } else {
            ElMessage.error(res.data.msg || "注册失败");
            // 刷新验证码
            refreshCaptcha();
        }
    } catch (error) {
        console.error("注册错误:", error);
        ElMessage.error("网络错误，请稍后重试");
        // 刷新验证码
        refreshCaptcha();
    }
}

function goToLogin() {
    router.push("/login");
}

// 组件挂载时刷新验证码
onMounted(() => {
    refreshCaptcha();
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
.signup-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    max-width: 500px;
    margin: 0 auto;
    padding: 36px 28px;
    border-radius: 12px;
    background: #f7faff;
    box-shadow: 0 4px 24px rgba(0, 80, 180, 0.08);
    border: 1px solid #e3eefd;
    /* 让容器在父级中垂直居中 */
    position: relative;
    margin-top: 50px;
    margin-bottom: 50px;
}

h2 {
    color: #205ec9;
    text-align: center;
    margin-bottom: 28px;
    letter-spacing: 2px;
}

.form-group {
    margin-bottom: 22px;
    width: 100%;
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
    width: auto !important;
    min-width: 30px;
    max-width: 80px;
    margin-right: 12px;
    padding: 8px 6px;
    box-sizing: border-box;
}

.captcha-img {
    height: 38px;
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
    width: 100%;
}

.form-actions button {
    width: 48%;
    padding: 10px 0;
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
</style>
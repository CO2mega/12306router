import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import './assets/main.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 配置 Element Plus
app.use(ElementPlus, {
    locale: zhCn,
})

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')

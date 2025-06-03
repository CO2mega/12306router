import axios from 'axios';
import router from '../router'; // 直接导入路由实例

// 创建 axios 实例
const request = axios.create({
    baseURL: 'http://localhost:3000',
    timeout: 5000
});

// 请求拦截器
request.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器
request.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // token 过期或无效
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    router.push('/login');
                    break;
                default:
                    console.error('请求错误:', error);
            }
        }
        return Promise.reject(error);
    }
);

export default request;
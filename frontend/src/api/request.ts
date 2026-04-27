import axios from 'axios'

const service = axios.create({
  baseURL: '/api', // 这里的 /api 会被 vite 代理拦截
  timeout: 5000
})

// 响应拦截器：可以统一处理报错
service.interceptors.response.use(
  response => response.data,
  error => {
    console.error('网络请求错误:', error)
    return Promise.reject(error)
  }
)

export default service
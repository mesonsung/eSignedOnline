import axios from 'axios'

const api = axios.create({
  baseURL: '/api', // 使用相對路徑，通過 Nginx 代理到後端
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 確保每次請求都包含最新的 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除本地存儲的 token
      localStorage.removeItem('token')
      // 重定向到登入頁面
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
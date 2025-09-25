import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    try {
      // 將 credentials 轉換為 URL-encoded 格式
      const formData = new URLSearchParams()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      const { access_token } = response.data
      
      token.value = access_token
      localStorage.setItem('token', access_token)
      
      // 設定 axios 預設 header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // 獲取用戶資訊
      await fetchUser()
      
      return response.data
    } catch (error) {
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const activate = async (username, activationCode) => {
    try {
      const response = await api.post('/auth/activate', {
        username,
        activation_code: activationCode
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  const logout = async () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
  }

  // 初始化時檢查 token
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser().catch(() => {
      logout()
    })
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    activate,
    fetchUser,
    logout
  }
})

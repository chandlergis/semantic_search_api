import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types/auth'
import { userService } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 初始化认证状态（从localStorage读取）
  const initAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  // 登录
  const login = async (credentials: LoginRequest) => {
    isLoading.value = true
    
    try {
      const response: AuthResponse = await userService.login(credentials)
      
      // 保存认证信息 - 后端只返回token，用户信息需要从email推断
      token.value = response.access_token
      user.value = {
        id: '', // 临时值，实际应用中可能需要另外获取
        username: credentials.email.split('@')[0], // 从邮箱推断用户名
        email: credentials.email,
        created_at: new Date().toISOString(),
        is_active: true
      }
      
      // 持久化到localStorage
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('auth_user', JSON.stringify(user.value))
      
      return { success: true }
    } catch (error: any) {
      console.error('登录失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '登录失败，请检查邮箱和密码' 
      }
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const register = async (userData: RegisterRequest) => {
    isLoading.value = true
    
    try {
      await userService.register(userData)
      
      // 注册成功后需要再登录获取token
      const loginResult = await login({
        email: userData.email,
        password: userData.password
      })
      
      return loginResult
    } catch (error: any) {
      console.error('注册失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '注册失败，请稍后重试' 
      }
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    
    // 清除localStorage
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  // 更新用户信息
  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('auth_user', JSON.stringify(user.value))
    }
  }

  // 检查token是否有效
  const validateToken = async () => {
    if (!token.value) return false
    
    try {
      // 这里可以调用API验证token
      // const response = await userService.validateToken()
      return true
    } catch (error) {
      // token无效，清除认证信息
      logout()
      return false
    }
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    initAuth,
    login,
    register,
    logout,
    updateUser,
    validateToken
  }
})

// 类型导出
export type AuthStore = ReturnType<typeof useAuthStore>
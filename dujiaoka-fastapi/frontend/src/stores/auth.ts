import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import type { User } from '@/types/auth'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_superuser || false)

  // 初始化认证状态
  const initAuth = () => {
    const savedToken = Cookies.get('token')
    if (savedToken) {
      token.value = savedToken
      // 获取用户信息
      loadUserInfo()
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login(username, password)
      const { access_token } = response.data

      token.value = access_token
      Cookies.set('token', access_token, { expires: 7 }) // 7天过期

      // 获取用户信息
      await loadUserInfo()

      return response
    } catch (error) {
      throw error
    }
  }

  // 注册
  const register = async (userData: {
    username: string
    email: string
    password: string
    full_name?: string
    phone?: string
  }) => {
    try {
      const response = await authApi.register(userData)
      return response
    } catch (error) {
      throw error
    }
  }

  // 登出
  const logout = () => {
    token.value = null
    user.value = null
    Cookies.remove('token')
  }

  // 加载用户信息
  const loadUserInfo = async () => {
    if (!token.value) return

    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (error) {
      // Token可能已过期或API不可用，重置状态但不抛出错误
      console.warn('加载用户信息失败，后端API可能未启动:', error)
      // 不在此处自动登出，让用户可以手动操作
      // logout()
    }
  }

  // 更新用户信息
  const updateUser = async (userData: Partial<User>) => {
    try {
      const response = await authApi.updateCurrentUser(userData)
      user.value = response.data
      return response
    } catch (error) {
      throw error
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      const response = await authApi.changePassword(oldPassword, newPassword)
      return response
    } catch (error) {
      throw error
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    initAuth,
    login,
    register,
    logout,
    loadUserInfo,
    updateUser,
    changePassword,
  }
})

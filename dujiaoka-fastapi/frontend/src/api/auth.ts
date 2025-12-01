import http from './http'
import type { User, LoginRequest, RegisterRequest, Token } from '@/types/auth'

export const authApi = {
  // 登录
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    return http.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 注册
  register: (userData: RegisterRequest) => {
    return http.post<User>('/auth/register', userData)
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return http.get<User>('/auth/me')
  },

  // 更新当前用户信息
  updateCurrentUser: (userData: Partial<User>) => {
    return http.put<User>('/auth/me', userData)
  },

  // 修改密码
  changePassword: (oldPassword: string, newPassword: string) => {
    return http.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },
}

// 认证相关类型定义

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  phone?: string
  avatar?: string
  balance: number
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  last_login?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
  phone?: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface TokenData {
  username?: string
}

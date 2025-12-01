// 用户相关类型定义

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

export interface UserUpdate {
  email?: string
  full_name?: string
  phone?: string
  avatar?: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  phone?: string
}

export interface UserList {
  items: User[]
  total: number
  page: number
  size: number
}

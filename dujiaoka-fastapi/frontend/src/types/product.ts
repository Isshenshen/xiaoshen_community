// 商品相关类型定义

export interface Category {
  id: number
  name: string
  description?: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Product {
  id: number
  name: string
  description?: string
  price: number
  original_price?: number
  category_id?: number
  stock: number
  sold_count: number
  auto_delivery: boolean
  is_active: boolean
  sort_order: number
  image_url?: string
  created_at: string
  updated_at: string
  category?: Category
}

export interface ProductList {
  items: Product[]
  total: number
  page: number
  size: number
}

export interface ProductCreate {
  name: string
  description?: string
  price: number
  original_price?: number
  category_id?: number
  stock: number
  auto_delivery: boolean
  is_active: boolean
  sort_order: number
  image_url?: string
}

export interface ProductUpdate {
  name?: string
  description?: string
  price?: number
  original_price?: number
  category_id?: number
  stock?: number
  auto_delivery?: boolean
  is_active?: boolean
  sort_order?: number
  image_url?: string
}

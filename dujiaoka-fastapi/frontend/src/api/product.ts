import http from './http'
import type { Product, Category, ProductList } from '@/types/product'

export interface ProductCreateData {
  name: string
  description?: string
  price: number
  original_price?: number | null
  category_id?: number | null
  stock: number
  auto_delivery?: boolean
  is_active?: boolean
  sort_order?: number
  image_url?: string
  project_url?: string
  download_url?: string
  tech_stack?: string
  project_type?: string
  difficulty_level?: string
}

export interface ProductUpdateData extends Partial<ProductCreateData> {}

export const productApi = {
  // 获取商品列表
  getProducts: (params?: {
    skip?: number
    limit?: number
    category_id?: number
    search?: string
    is_active?: boolean
  }) => {
    return http.get<ProductList>('/products/', { params })
  },

  // 获取商品详情
  getProduct: (productId: number) => {
    return http.get<Product>(`/products/${productId}`)
  },

  // 获取分类列表
  getCategories: () => {
    return http.get<Category[]>('/products/categories')
  },

  // 创建商品（管理员）
  createProduct: (data: ProductCreateData) => {
    return http.post<Product>('/products/', data)
  },

  // 更新商品（管理员）
  updateProduct: (productId: number, data: ProductUpdateData) => {
    return http.put<Product>(`/products/${productId}`, data)
  },

  // 删除商品（管理员）
  deleteProduct: (productId: number) => {
    return http.delete<{ message: string }>(`/products/${productId}`)
  },

  // 更新商品库存（管理员）
  updateStock: (productId: number, quantity: number) => {
    return http.post<{ message: string; stock: number }>(
      `/products/${productId}/stock`,
      null,
      { params: { quantity } }
    )
  },

  // 创建分类（管理员）
  createCategory: (data: { name: string; description?: string; sort_order?: number }) => {
    return http.post<Category>('/products/categories', data)
  },

  // 更新分类（管理员）
  updateCategory: (categoryId: number, data: { name?: string; description?: string; sort_order?: number }) => {
    return http.put<Category>(`/products/categories/${categoryId}`, data)
  },

  // 删除分类（管理员）
  deleteCategory: (categoryId: number) => {
    return http.delete<{ message: string }>(`/products/categories/${categoryId}`)
  },
}

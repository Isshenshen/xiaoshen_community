// 订单相关类型定义

export interface Order {
  id: number
  order_number: string
  user_id: number
  product_id: number
  product_name: string
  product_price: number
  quantity: number
  total_amount: number
  payment_method: string
  status: string
  delivery_content?: string
  delivered_at?: string
  user_note?: string
  admin_note?: string
  created_at: string
  updated_at: string
  paid_at?: string
  user?: {
    id: number
    username: string
    email: string
  }
  product?: {
    id: number
    name: string
    image_url?: string
  }
}

export interface OrderCreate {
  product_id: number
  quantity: number
  payment_method: string
  user_note?: string
}

export interface OrderUpdate {
  status?: string
  admin_note?: string
}

export interface OrderList {
  items: Order[]
  total: number
  page: number
  size: number
}

export interface CartItem {
  product_id: number
  quantity: number
  price?: number
  name?: string
  image_url?: string
}

export interface OrderSummary {
  items: CartItem[]
  total_amount: number
}

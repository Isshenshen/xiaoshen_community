import http from './http'
import type { Order, OrderCreate, OrderList, CartItem, OrderSummary } from '@/types/order'

export const orderApi = {
  // 获取订单列表
  getOrders: (params?: {
    skip?: number
    limit?: number
    status?: string
  }) => {
    return http.get<OrderList>('/orders/', { params })
  },

  // 获取订单详情
  getOrder: (orderId: number) => {
    return http.get<Order>(`/orders/${orderId}`)
  },

  // 创建订单
  createOrder: (orderData: OrderCreate) => {
    return http.post<Order>('/orders/', orderData)
  },

  // 从购物车创建订单
  createCartOrder: (items: CartItem[], paymentMethod: string, userNote?: string) => {
    return http.post<OrderSummary>('/orders/cart', {
      items,
      payment_method: paymentMethod,
      user_note: userNote,
    })
  },

  // 更新订单
  updateOrder: (orderId: number, orderData: Partial<Order>) => {
    return http.put<Order>(`/orders/${orderId}`, orderData)
  },

  // 支付订单
  payOrder: (orderId: number) => {
    return http.post<Order>(`/orders/${orderId}/pay`)
  },

  // 取消订单
  cancelOrder: (orderId: number) => {
    return http.post<Order>(`/orders/${orderId}/cancel`)
  },
}

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem } from '@/types/order'

export const useCartStore = defineStore('cart', () => {
  // 购物车商品列表
  const items = ref<CartItem[]>([])

  // 计算属性
  const totalItems = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalAmount = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  // 方法
  const addItem = (productId: number, quantity: number = 1, price: number = 0, name: string = '', imageUrl: string = '') => {
    const existingItem = items.value.find(item => item.product_id === productId)

    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({
        product_id: productId,
        quantity,
        price,
        name,
        image_url: imageUrl,
      })
    }
  }

  const removeItem = (productId: number) => {
    const index = items.value.findIndex(item => item.product_id === productId)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  const updateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      removeItem(productId)
      return
    }

    const item = items.value.find(item => item.product_id === productId)
    if (item) {
      item.quantity = quantity
    }
  }

  const clearCart = () => {
    items.value = []
  }

  const getItemCount = (productId: number) => {
    const item = items.value.find(item => item.product_id === productId)
    return item ? item.quantity : 0
  }

  return {
    items,
    totalItems,
    totalAmount,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    getItemCount,
  }
})

<template>
  <div class="cart">
    <div class="cart-header">
      <h2>购物车</h2>
      <el-button type="primary" @click="$router.push('/products')">
        继续购物
      </el-button>
    </div>

    <!-- 购物车为空 -->
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <el-empty description="购物车是空的">
        <el-button type="primary" @click="$router.push('/products')">
          去购物
        </el-button>
      </el-empty>
    </div>

    <!-- 购物车内容 -->
    <div v-else class="cart-content">
      <div class="cart-items">
        <div
          v-for="item in cartProducts"
          :key="item.id"
          class="cart-item"
        >
          <div class="item-info">
            <div class="item-image">
              <img
                :src="item.image_url || placeholderImage"
                :alt="item.name"
                @error="handleImageError"
              />
            </div>
            <div class="item-details">
              <h3>{{ item.name }}</h3>
              <p class="item-description">{{ item.description }}</p>
              <p class="item-price">¥{{ item.price }}</p>
            </div>
          </div>

          <div class="item-controls">
            <div class="quantity-control">
              <el-button
                size="small"
                @click="decreaseQuantity(item.id)"
                :disabled="cartStore.getItemCount(item.id) <= 1"
              >
                -
              </el-button>
              <span class="quantity">{{ cartStore.getItemCount(item.id) }}</span>
              <el-button
                size="small"
                @click="increaseQuantity(item.id)"
              >
                +
              </el-button>
            </div>

            <div class="item-total">
              ¥{{ (item.price * cartStore.getItemCount(item.id)).toFixed(2) }}
            </div>

            <el-button
              type="danger"
              size="small"
              @click="removeItem(item.id, item.name)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 结算区域 -->
      <div class="cart-summary">
        <div class="summary-info">
          <div class="summary-row">
            <span>商品数量:</span>
            <span>{{ totalQuantity }} 件</span>
          </div>
          <div class="summary-row total">
            <span>总计:</span>
            <span class="total-amount">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>

        <div class="checkout-actions">
          <el-button size="large" @click="clearCart">
            清空购物车
          </el-button>
          <el-button
            type="primary"
            size="large"
            @click="checkout"
            :disabled="cartStore.items.length === 0"
          >
            结算 ({{ totalQuantity }})
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import placeholderImage from '@/assets/images/placeholder.svg'
import { useCartStore } from '@/stores/cart'
import { productApi } from '@/api/product'
import type { Product } from '@/types/product'

const router = useRouter()
const cartStore = useCartStore()

// 获取购物车商品的详细信息
const cartProducts = ref<Product[]>([])
const loading = ref(false)

// 计算属性
const totalQuantity = computed(() => cartStore.totalItems)
const totalAmount = computed(() => cartStore.totalAmount)

// 获取购物车商品详情
const loadCartProducts = async () => {
  loading.value = true
  try {
    const productIds = cartStore.items.map(item => item.product_id)
    if (productIds.length === 0) {
      cartProducts.value = []
      return
    }

    // 获取所有商品信息
    const promises = productIds.map(id => productApi.getProduct(id))
    const responses = await Promise.all(promises)

    cartProducts.value = responses.map((response, index) => {
      const product = response.data
      const cartItem = cartStore.items[index]
      return {
        ...product,
        cart_quantity: cartItem.quantity,
      }
    })
  } catch (error) {
    ElMessage.error('加载购物车商品失败')
  } finally {
    loading.value = false
  }
}

// 方法
const increaseQuantity = (productId: number) => {
  const currentQuantity = cartStore.getItemCount(productId)
  cartStore.updateQuantity(productId, currentQuantity + 1)
}

const decreaseQuantity = (productId: number) => {
  const currentQuantity = cartStore.getItemCount(productId)
  if (currentQuantity > 1) {
    cartStore.updateQuantity(productId, currentQuantity - 1)
  }
}

const removeItem = async (productId: number, productName: string) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 "${productName}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    cartStore.removeItem(productId)
    ElMessage.success('已删除')
    loadCartProducts()
  } catch {
    // 用户取消
  }
}

const clearCart = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空购物车吗？',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    cartStore.clearCart()
    cartProducts.value = []
    ElMessage.success('购物车已清空')
  } catch {
    // 用户取消
  }
}

const checkout = () => {
  if (cartStore.items.length === 0) {
    ElMessage.warning('购物车为空')
    return
  }

  // 跳转到订单创建页面或直接创建订单
  router.push('/checkout')
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = placeholderImage
}

// 生命周期
onMounted(() => {
  loadCartProducts()
})
</script>

<style scoped>
.cart {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.cart-header h2 {
  margin: 0;
  color: #303133;
}

.empty-cart {
  text-align: center;
  padding: 80px 20px;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 40px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: white;
}

.item-info {
  display: flex;
  gap: 15px;
  flex: 1;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.item-description {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.item-price {
  margin: 0;
  color: #f56c6c;
  font-weight: 500;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity {
  min-width: 30px;
  text-align: center;
  font-weight: 500;
}

.item-total {
  font-weight: 600;
  color: #f56c6c;
  min-width: 80px;
  text-align: right;
}

.cart-summary {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 30px;
  height: fit-content;
  position: sticky;
  top: 20px;
}

.summary-info {
  margin-bottom: 30px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
}

.summary-row.total {
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
  margin-top: 15px;
  font-size: 16px;
  font-weight: 600;
}

.total-amount {
  color: #f56c6c;
  font-size: 20px;
}

.checkout-actions {
  display: flex;
  gap: 15px;
}

@media (max-width: 768px) {
  .cart-content {
    grid-template-columns: 1fr;
  }

  .cart-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .item-controls {
    width: 100%;
    justify-content: space-between;
  }

  .cart-summary {
    position: static;
  }
}
</style>

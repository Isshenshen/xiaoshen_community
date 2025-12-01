<template>
  <div class="checkout">
    <div class="checkout-header">
      <h2>确认订单</h2>
      <el-steps :active="1" simple>
        <el-step title="确认订单" />
        <el-step title="支付" />
        <el-step title="完成" />
      </el-steps>
    </div>

    <div class="checkout-content">
      <el-row :gutter="40">
        <!-- 订单商品列表 -->
        <el-col :span="16">
          <el-card class="order-items-card">
            <template #header>
              <span>商品清单</span>
            </template>

            <div class="order-items">
              <!-- 模板订单 -->
              <div v-if="isTemplateOrder && orderTemplate" class="order-item">
                <div class="item-image">
                  <img
                    :src="placeholderImage"
                    alt="定制开发"
                  />
                </div>
                <div class="item-info">
                  <h4>{{ orderTemplate.title }}</h4>
                  <p class="item-description">{{ orderTemplate.description }}</p>
                  <el-tag type="warning">定制开发</el-tag>
                </div>
                <div class="item-price">
                  ¥{{ orderTemplate.price }}
                </div>
                <div class="item-quantity">
                  ×1
                </div>
                <div class="item-total">
                  ¥{{ orderTemplate.price }}
                </div>
              </div>

              <!-- 购物车商品 -->
              <div
                v-for="item in cartProducts"
                :key="item.id"
                class="order-item"
                v-else
              >
                <div class="item-image">
                  <img
                    :src="item.image_url || placeholderImage"
                    :alt="item.name"
                    @error="handleImageError"
                  />
                </div>
                <div class="item-info">
                  <h4>{{ item.name }}</h4>
                  <p class="item-description">{{ item.description }}</p>
                </div>
                <div class="item-price">
                  ¥{{ item.price }}
                </div>
                <div class="item-quantity">
                  ×{{ cartStore.getItemCount(item.id) }}
                </div>
                <div class="item-total">
                  ¥{{ (item.price * cartStore.getItemCount(item.id)).toFixed(2) }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- 买家留言 -->
          <el-card class="message-card">
            <template #header>
              <span>买家留言</span>
            </template>
            <el-input
              v-model="userNote"
              type="textarea"
              :rows="3"
              placeholder="选填：对本次交易的说明"
            />
          </el-card>
        </el-col>

        <!-- 订单结算 -->
        <el-col :span="8">
          <el-card class="order-summary">
            <template #header>
              <span>订单结算</span>
            </template>

            <div class="summary-details">
              <div class="summary-row">
                <span>商品数量:</span>
                <span>{{ totalQuantity }} 件</span>
              </div>
              <div class="summary-row total">
                <span>商品总价:</span>
                <span>¥{{ totalAmount.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 支付方式选择 -->
            <div class="payment-methods">
              <h4>选择支付方式</h4>
              <el-radio-group v-model="paymentMethod" class="payment-options">
                <el-radio value="balance" class="payment-option">
                  <div class="payment-info">
                    <span class="payment-name">余额支付</span>
                    <span class="payment-desc">当前余额: ¥{{ userBalance }}</span>
                  </div>
                </el-radio>
                <el-radio value="alipay" class="payment-option">
                  <div class="payment-info">
                    <span class="payment-name">支付宝</span>
                    <span class="payment-desc">推荐使用</span>
                  </div>
                </el-radio>
                <el-radio value="wechat" class="payment-option">
                  <div class="payment-info">
                    <span class="payment-name">微信支付</span>
                    <span class="payment-desc">快速支付</span>
                  </div>
                </el-radio>
              </el-radio-group>
            </div>

            <div class="checkout-actions">
              <el-button size="large" @click="$router.push('/cart')">
                返回购物车
              </el-button>
              <el-button
                type="primary"
                size="large"
                @click="submitOrder"
                :loading="submitting"
                :disabled="!canSubmit"
              >
                提交订单
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import placeholderImage from '@/assets/images/placeholder.svg'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { productApi } from '@/api/product'
import { orderApi } from '@/api/order'
import type { Product } from '@/types/product'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

// 数据
const cartProducts = ref<Product[]>([])
const loading = ref(false)
const submitting = ref(false)
const userNote = ref('')
const paymentMethod = ref('balance')
const userBalance = ref(1000) // 模拟余额

// 模板订单相关
const orderTemplate = ref<any>(null)
const isTemplateOrder = ref(false)

// 计算属性
const totalQuantity = computed(() => {
  return isTemplateOrder.value ? 1 : cartStore.totalItems
})
const totalAmount = computed(() => {
  return isTemplateOrder.value ? (orderTemplate.value?.price || 0) : cartStore.totalAmount
})
const canSubmit = computed(() => {
  return (cartProducts.value.length > 0 || isTemplateOrder.value) && paymentMethod.value
})

// 方法
const loadCartProducts = async () => {
  loading.value = true
  try {
    const productIds = cartStore.items.map(item => item.product_id)
    if (productIds.length === 0) {
      router.push('/cart')
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
    ElMessage.error('加载商品信息失败')
    router.push('/cart')
  } finally {
    loading.value = false
  }
}

const submitOrder = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  if (paymentMethod.value === 'balance' && userBalance.value < totalAmount.value) {
    ElMessage.error('余额不足')
    return
  }

  submitting.value = true
  try {
    // 创建订单
    const orderData = {
      items: cartStore.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      payment_method: paymentMethod.value,
      user_note: userNote.value,
    }

    const response = await orderApi.createCartOrder(
      orderData.items,
      orderData.payment_method,
      orderData.user_note
    )

    const order = response.data

    // 清空购物车
    cartStore.clearCart()

    // 跳转到支付页面或订单详情
    if (paymentMethod.value === 'balance') {
      // 余额支付直接完成
      ElMessage.success('订单提交成功！')
      router.push(`/orders/${order.id}`)
    } else {
      // 其他支付方式跳转到支付页面
      ElMessage.success('订单提交成功，正在跳转到支付页面...')
      router.push(`/orders/${order.id}`)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建订单失败')
  } finally {
    submitting.value = false
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = placeholderImage
}

// 生命周期
onMounted(() => {
  // 检查是否是模板订单
  const route = useRoute()
  const query = route.query

  if (query.templateId && query.type === 'template') {
    isTemplateOrder.value = true
    // TODO: 加载模板信息
    orderTemplate.value = {
      id: query.templateId,
      title: '定制开发项目',
      price: 1999.00,
      description: '管理员创建的定制开发项目',
    }
  } else if (cartStore.items.length === 0) {
    router.push('/cart')
    return
  }

  loadCartProducts()
})
</script>

<style scoped>
.checkout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.checkout-header {
  margin-bottom: 40px;
}

.checkout-header h2 {
  margin-bottom: 20px;
  color: #303133;
}

.checkout-content {
  margin-top: 30px;
}

.order-items-card,
.message-card,
.order-summary {
  margin-bottom: 30px;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafbfc;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  margin-right: 15px;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  margin-right: 15px;
}

.item-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.item-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
  line-height: 1.4;
}

.item-price,
.item-quantity,
.item-total {
  text-align: center;
  min-width: 80px;
}

.item-price {
  color: #f56c6c;
  font-weight: 500;
}

.item-total {
  color: #f56c6c;
  font-weight: 600;
}

.message-card .el-textarea {
  margin-top: 10px;
}

.summary-details {
  margin-bottom: 30px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 0;
}

.summary-row.total {
  border-top: 2px solid #ebeef5;
  padding-top: 15px;
  margin-top: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.payment-methods {
  margin-bottom: 30px;
}

.payment-methods h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.payment-options {
  width: 100%;
}

.payment-option {
  display: block;
  margin-bottom: 10px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-option:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.payment-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payment-name {
  font-weight: 500;
  color: #303133;
}

.payment-desc {
  font-size: 12px;
  color: #909399;
}

.checkout-actions {
  display: flex;
  gap: 15px;
}

@media (max-width: 768px) {
  .checkout {
    padding: 20px 10px;
  }

  .checkout-content .el-col {
    margin-bottom: 20px;
  }

  .checkout-content .el-col:last-child {
    margin-bottom: 0;
  }

  .order-item {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }

  .item-info {
    margin-right: 0;
  }

  .checkout-actions {
    flex-direction: column;
  }
}
</style>

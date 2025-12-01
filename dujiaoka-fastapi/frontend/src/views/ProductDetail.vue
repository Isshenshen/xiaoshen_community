<template>
  <div class="product-detail" v-loading="loading">
    <el-row :gutter="40">
      <!-- 商品图片 -->
      <el-col :span="10">
        <div class="product-image">
          <el-image
            :src="product?.image_url || placeholderImage"
            :alt="product?.name"
            fit="cover"
            @error="handleImageError"
          />
        </div>
      </el-col>

      <!-- 商品信息 -->
      <el-col :span="14">
        <div class="product-info">
          <h1 class="product-name">{{ product?.name }}</h1>

          <div class="product-price">
            <span class="current-price">¥{{ product?.price }}</span>
            <span class="original-price" v-if="product?.original_price">
              ¥{{ product.original_price }}
            </span>
          </div>

          <div class="product-meta">
            <div class="meta-item">
              <span class="label">库存:</span>
              <span class="value">{{ product?.stock }}</span>
            </div>
            <div class="meta-item">
              <span class="label">已售:</span>
              <span class="value">{{ product?.sold_count }}</span>
            </div>
            <div class="meta-item" v-if="product?.category">
              <span class="label">分类:</span>
              <el-tag>{{ product.category.name }}</el-tag>
            </div>
          </div>

          <div class="product-description">
            <h3>商品描述</h3>
            <p>{{ product?.description || '暂无描述' }}</p>
          </div>

          <!-- 购买选项 -->
          <div class="purchase-options">
            <div class="quantity-selector">
              <span>数量:</span>
              <el-input-number
                v-model="quantity"
                :min="1"
                :max="product?.stock || 1"
                size="small"
              />
            </div>

            <div class="total-price">
              <span>总计: </span>
              <span class="price">¥{{ totalPrice }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :disabled="!canPurchase"
              @click="handlePurchase"
            >
              {{ canPurchase ? '立即购买源码' : purchaseButtonText }}
            </el-button>
            <el-button size="large" @click="addToCart">
              加入购物车
            </el-button>
          </div>

          <!-- 商品状态提示 -->
          <div v-if="!product?.is_active" class="status-warning">
            <el-alert
              title="商品已下架"
              type="warning"
              :closable="false"
            />
          </div>
          <div v-else-if="product?.stock <= 0" class="status-warning">
            <el-alert
              title="商品缺货"
              type="error"
              :closable="false"
            />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import placeholderImage from '@/assets/images/placeholder.svg'
import { productApi } from '@/api/product'
import { orderApi } from '@/api/order'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import type { Product } from '@/types/product'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

// 数据
const product = ref<Product | null>(null)
const quantity = ref(1)
const loading = ref(true)

// 计算属性
const totalPrice = computed(() => {
  if (!product.value) return 0
  return (product.value.price * quantity.value).toFixed(2)
})

const canPurchase = computed(() => {
  return (
    product.value?.is_active &&
    (product.value?.stock || 0) > 0 &&
    authStore.isAuthenticated
  )
})

const purchaseButtonText = computed(() => {
  if (!authStore.isAuthenticated) return '请先登录'
  if (!product.value?.is_active) return '商品已下架'
  if ((product.value?.stock || 0) <= 0) return '商品缺货'
  return '立即购买'
})

// 方法
const loadProduct = async () => {
  try {
    const productId = parseInt(route.params.id as string)
    const response = await productApi.getProduct(productId)
    product.value = response.data
  } catch (error) {
    ElMessage.error('加载商品失败')
    router.push('/products')
  } finally {
    loading.value = false
  }
}

const handlePurchase = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (!canPurchase.value) {
    return
  }

  try {
    await ElMessageBox.confirm(
              `确认购买 ${product.value?.name} 源码 × ${quantity.value}？\n总计: ¥${totalPrice.value}`,
      '确认购买',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 创建订单
    try {
      const orderData = {
        product_id: product.value!.id,
        quantity: quantity.value,
        payment_method: 'balance', // 默认余额支付
      }

      const response = await orderApi.createOrder(orderData)
      const order = response.data

      ElMessage.success('订单创建成功，正在跳转...')
      router.push(`/orders/${order.id}`)
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '创建订单失败')
    }

  } catch (error) {
    // 用户取消操作
  }
}

const addToCart = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (!product.value) return

  if (!product.value.is_active) {
    ElMessage.warning('商品已下架')
    return
  }

  if ((product.value.stock || 0) <= 0) {
    ElMessage.warning('商品缺货')
    return
  }

  cartStore.addItem(
    product.value.id,
    quantity.value,
    product.value.price,
    product.value.name,
    product.value.image_url
  )
  ElMessage.success('已添加到购物车')
}

const handleImageError = () => {
  if (product.value) {
    product.value.image_url = placeholderImage
  }
}

// 生命周期
onMounted(() => {
  loadProduct()
})
</script>

<style scoped>
.product-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.product-image {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-info {
  padding-left: 20px;
}

.product-name {
  margin: 0 0 20px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.current-price {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
}

.original-price {
  font-size: 20px;
  color: #909399;
  text-decoration: line-through;
}

.product-meta {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: #606266;
  font-size: 14px;
}

.value {
  color: #303133;
  font-weight: 500;
}

.product-description {
  margin-bottom: 30px;
}

.product-description h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #303133;
}

.product-description p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.purchase-options {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.total-price {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  font-size: 18px;
  font-weight: 500;
}

.total-price .price {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.status-warning {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .product-detail {
    padding: 20px 10px;
  }

  .product-info {
    padding-left: 0;
    padding-top: 20px;
  }

  .product-name {
    font-size: 24px;
  }

  .current-price {
    font-size: 28px;
  }

  .product-meta {
    flex-direction: column;
    gap: 10px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .total-price {
    justify-content: center;
  }
}
</style>

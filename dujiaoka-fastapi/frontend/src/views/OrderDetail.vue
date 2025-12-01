<template>
  <div class="order-detail" v-loading="loading">
    <div class="order-header">
      <div class="header-info">
        <h2>订单详情</h2>
        <p class="order-number">订单号: {{ order?.order_number }}</p>
      </div>
      <el-tag :type="getStatusType(order?.status)">
        {{ getStatusText(order?.status) }}
      </el-tag>
    </div>

    <!-- 订单进度 -->
    <div class="order-progress">
      <el-steps :active="getActiveStep(order?.status)" align-center>
        <el-step title="待支付" description="订单已创建" />
        <el-step title="已支付" description="支付完成" />
        <el-step title="已发货" description="源码已发放" />
        <el-step title="已完成" description="交易完成" />
      </el-steps>
    </div>

    <div class="order-content">
      <el-row :gutter="40">
        <!-- 订单信息 -->
        <el-col :span="16">
          <!-- 商品信息 -->
          <el-card class="product-card">
            <template #header>
              <span>商品信息</span>
            </template>

            <div class="product-info">
              <div class="product-image">
                <img
                  :src="order?.product?.image_url || placeholderImage"
                  :alt="order?.product_name"
                  @error="handleImageError"
                />
              </div>
              <div class="product-details">
                <h3>{{ order?.product_name }}</h3>
                <p class="product-price">单价: ¥{{ order?.product_price }}</p>
                <p class="quantity">数量: {{ order?.quantity }}</p>
                <p class="total-price">小计: ¥{{ orderTotal }}</p>
              </div>
            </div>
          </el-card>

          <!-- 订单信息 -->
          <el-card class="order-info-card">
            <template #header>
              <span>订单信息</span>
            </template>

            <div class="info-grid">
              <div class="info-item">
                <span class="label">订单号:</span>
                <span class="value">{{ order?.order_number }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ formatTime(order?.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">支付方式:</span>
                <span class="value">{{ getPaymentMethodText(order?.payment_method) }}</span>
              </div>
              <div class="info-item" v-if="order?.paid_at">
                <span class="label">支付时间:</span>
                <span class="value">{{ formatTime(order?.paid_at) }}</span>
              </div>
              <div class="info-item" v-if="order?.delivered_at">
                <span class="label">发货时间:</span>
                <span class="value">{{ formatTime(order?.delivered_at) }}</span>
              </div>
              <div class="info-item" v-if="order?.user_note">
                <span class="label">买家留言:</span>
                <span class="value">{{ order?.user_note }}</span>
              </div>
              <div class="info-item" v-if="order?.admin_note">
                <span class="label">管理员备注:</span>
                <span class="value">{{ order?.admin_note }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 侧边栏 -->
        <el-col :span="8">
          <!-- 价格明细 -->
          <el-card class="price-card">
            <template #header>
              <span>价格明细</span>
            </template>

            <div class="price-breakdown">
              <div class="price-row">
                <span>商品金额</span>
                <span>¥{{ orderTotal }}</span>
              </div>
              <div class="price-row total">
                <span>总计</span>
                <span class="total-amount">¥{{ order?.total_amount }}</span>
              </div>
            </div>
          </el-card>

          <!-- 操作按钮 -->
          <el-card class="actions-card">
            <template #header>
              <span>操作</span>
            </template>

            <div class="action-buttons">
              <el-button
                v-if="order?.status === 'pending'"
                type="primary"
                @click="payOrder"
                block
              >
                立即支付
              </el-button>

              <el-button
                v-if="order?.status === 'delivered' && order?.delivery_content"
                type="success"
                @click="showDeliveryContent"
                block
              >
                查看源码下载链接
              </el-button>

              <el-button
                v-if="canCancelOrder"
                type="danger"
                @click="cancelOrder"
                block
              >
                取消订单
              </el-button>

              <el-button @click="$router.push('/orders')" block>
                返回订单列表
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 源码下载链接对话框 -->
    <el-dialog
      v-model="deliveryDialogVisible"
      title="源码下载信息"
      width="600px"
    >
      <div class="delivery-content">
        <el-alert
          title="下载说明"
          description="以下是您的源码下载链接，请妥善保存。如有问题请联系客服。"
          type="success"
          :closable="false"
        />

        <div class="download-links">
          <pre>{{ order?.delivery_content }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="deliveryDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyDeliveryContent">
          复制下载链接
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import placeholderImage from '@/assets/images/placeholder.svg'

const route = useRoute()

// 数据
const order = ref(null)
const loading = ref(true)
const deliveryDialogVisible = ref(false)

// 计算属性
const orderTotal = computed(() => {
  if (!order.value) return '0.00'
  return (order.value.product_price * order.value.quantity).toFixed(2)
})

const canCancelOrder = computed(() => {
  return order.value?.status === 'pending'
})

// 方法
const loadOrder = async () => {
  try {
    const orderId = route.params.id
    // TODO: 调用API获取订单详情
    // 这里使用模拟数据
    order.value = {
      id: orderId,
      order_number: 'ORD20241201001',
      product_name: 'Vue3 + FastAPI全栈博客系统',
      product_price: 99.00,
      quantity: 1,
      total_amount: 99.00,
      payment_method: 'balance',
      status: 'delivered',
      created_at: '2024-12-01T10:00:00Z',
      paid_at: '2024-12-01T10:05:00Z',
      delivered_at: '2024-12-01T10:10:00Z',
      delivery_content: `感谢购买！您的源码项目已准备就绪。

项目信息：
- 商品名称: Vue3 + FastAPI全栈博客系统
- 购买数量: 1
- 订单号: ORD20241201001

下载链接：
https://download.example.com/project/vue-blog-system.zip

解压密码: codehub2024

技术支持QQ: 123456789`,
      product: {
        image_url: '/product1.jpg',
      },
    }
  } catch (error) {
    ElMessage.error('加载订单详情失败')
  } finally {
    loading.value = false
  }
}

const getActiveStep = (status: string) => {
  const statusMap = {
    pending: 0,
    paid: 1,
    delivered: 2,
    cancelled: 3,
    refunded: 3,
  }
  return statusMap[status] || 0
}

const getStatusType = (status: string) => {
  const statusMap = {
    pending: 'warning',
    paid: 'info',
    delivered: 'success',
    cancelled: 'danger',
    refunded: 'danger',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待支付',
    paid: '已支付',
    delivered: '已发货',
    cancelled: '已取消',
    refunded: '已退款',
  }
  return statusMap[status] || status
}

const getPaymentMethodText = (method: string) => {
  const methodMap = {
    balance: '余额支付',
    alipay: '支付宝',
    wechat: '微信支付',
  }
  return methodMap[method] || method
}

const payOrder = () => {
  // TODO: 跳转到支付页面
  ElMessage.info('支付功能开发中...')
}

const cancelOrder = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消此订单吗？',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API取消订单
    ElMessage.success('订单已取消')
    loadOrder()
  } catch {
    // 用户取消
  }
}

const showDeliveryContent = () => {
  deliveryDialogVisible.value = true
}

const copyDeliveryContent = async () => {
  if (!order.value?.delivery_content) return

  try {
    await navigator.clipboard.writeText(order.value.delivery_content)
    ElMessage.success('下载信息已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = placeholderImage
}

// 生命周期
onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.order-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-info h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.order-number {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.order-progress {
  margin-bottom: 40px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.order-content {
  margin-top: 30px;
}

.product-card,
.order-info-card {
  margin-bottom: 30px;
}

.product-info {
  display: flex;
  gap: 20px;
}

.product-image {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-details h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.product-price,
.quantity,
.total-price {
  margin: 8px 0;
  color: #606266;
}

.total-price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  width: 100px;
  color: #909399;
  font-weight: 500;
}

.value {
  flex: 1;
  color: #303133;
}

.price-card,
.actions-card {
  margin-bottom: 30px;
}

.price-breakdown {
  padding: 20px 0;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 0;
}

.price-row.total {
  border-top: 2px solid #ebeef5;
  padding-top: 20px;
  margin-top: 20px;
  font-size: 18px;
  font-weight: 600;
}

.total-amount {
  color: #f56c6c;
  font-size: 24px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.delivery-content {
  padding: 20px 0;
}

.download-links {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.download-links pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #303133;
}

@media (max-width: 768px) {
  .order-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .product-info {
    flex-direction: column;
    text-align: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    gap: 5px;
  }

  .label {
    width: auto;
  }
}
</style>

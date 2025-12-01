<template>
  <div class="orders">
    <div class="page-header">
      <h2>我的订单</h2>
      <el-button type="primary" @click="$router.push('/products')">
        继续购物
      </el-button>
    </div>

    <!-- 状态筛选 -->
    <div class="status-filter">
      <el-radio-group v-model="statusFilter" @change="handleStatusChange">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="pending">待支付</el-radio-button>
        <el-radio-button label="paid">已支付</el-radio-button>
        <el-radio-button label="delivered">已发货</el-radio-button>
        <el-radio-button label="cancelled">已取消</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 订单列表 -->
    <div class="orders-list">
      <el-card
        v-for="order in orders"
        :key="order.id"
        class="order-card"
        shadow="hover"
      >
        <template #header>
          <div class="order-header">
            <div class="order-info">
              <span class="order-number">订单号: {{ order.order_number }}</span>
              <span class="order-time">{{ formatTime(order.created_at) }}</span>
            </div>
            <el-tag :type="getStatusType(order.status)">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>
        </template>

        <div class="order-content">
          <div class="product-info">
            <div class="product-image">
              <img
                :src="order.product?.image_url || placeholderImage"
                :alt="order.product?.name"
                @error="handleImageError"
              />
            </div>
            <div class="product-details">
              <h3>{{ order.product_name }}</h3>
              <p class="product-price">¥{{ order.product_price }}</p>
              <p class="quantity">数量: {{ order.quantity }}</p>
            </div>
          </div>

          <div class="order-total">
            <div class="total-amount">
              <span class="label">总金额:</span>
              <span class="amount">¥{{ order.total_amount }}</span>
            </div>
            <div class="payment-method">
              <span class="label">支付方式:</span>
              <span class="method">{{ getPaymentMethodText(order.payment_method) }}</span>
            </div>
          </div>
        </div>

        <template #footer>
          <div class="order-actions">
            <el-button size="small" @click="viewOrderDetail(order.id)">
              查看详情
            </el-button>

            <template v-if="order.status === 'pending'">
              <el-button type="primary" size="small" @click="payOrder(order)">
                立即支付
              </el-button>
              <el-button size="small" @click="cancelOrder(order)">
                取消订单
              </el-button>
            </template>

            <template v-if="order.status === 'paid'">
              <el-button size="small" @click="remindDelivery(order)">
                提醒发货
              </el-button>
            </template>

            <template v-if="order.status === 'delivered' && order.delivery_content">
              <el-button type="success" size="small" @click="viewDelivery(order)">
                查看源码
              </el-button>
            </template>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 空状态 -->
    <div v-if="orders.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无订单">
        <el-button type="primary" @click="$router.push('/products')">
          去购物
        </el-button>
      </el-empty>
    </div>

    <!-- 卡密查看对话框 -->
    <el-dialog
      v-model="deliveryDialogVisible"
      title="卡密信息"
      width="500px"
    >
      <div class="delivery-content">
        <pre>{{ selectedOrder?.delivery_content }}</pre>
      </div>
      <template #footer>
        <el-button @click="deliveryDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyDeliveryContent">
          复制卡密
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import placeholderImage from '@/assets/images/placeholder.svg'
import { orderApi } from '@/api/order'
import type { Order } from '@/types/order'

const orders = ref<Order[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const statusFilter = ref('')
const loading = ref(false)
const deliveryDialogVisible = ref(false)
const selectedOrder = ref<Order | null>(null)

// 计算属性
const skip = computed(() => (currentPage.value - 1) * pageSize.value)

// 方法
const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: pageSize.value,
      status: statusFilter.value || undefined,
    }

    const response = await orderApi.getOrders(params)
    orders.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const handleStatusChange = () => {
  currentPage.value = 1
  loadOrders()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadOrders()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadOrders()
}

const viewOrderDetail = (orderId: number) => {
  router.push(`/orders/${orderId}`)
}

const payOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      `确认支付 ¥${order.total_amount}？`,
      '确认支付',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await orderApi.payOrder(order.id)
    ElMessage.success('支付成功')
    loadOrders()
  } catch (error) {
    // 用户取消或支付失败
  }
}

const cancelOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      '确认取消此订单？',
      '取消订单',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await orderApi.cancelOrder(order.id)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (error) {
    // 用户取消
  }
}

const remindDelivery = (order: Order) => {
  ElMessage.info('已提醒商家发货')
}

const viewDelivery = (order: Order) => {
  selectedOrder.value = order
  deliveryDialogVisible.value = true
}

const copyDeliveryContent = async () => {
  if (!selectedOrder.value?.delivery_content) return

  try {
    await navigator.clipboard.writeText(selectedOrder.value.delivery_content)
    ElMessage.success('卡密已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    paid: 'info',
    delivered: 'success',
    cancelled: 'danger',
    refunded: 'danger',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待支付',
    paid: '已支付',
    delivered: '已发货',
    cancelled: '已取消',
    refunded: '已退款',
  }
  return statusMap[status] || status
}

const getPaymentMethodText = (method: string) => {
  const methodMap: Record<string, string> = {
    balance: '余额支付',
    alipay: '支付宝',
    wechat: '微信支付',
  }
  return methodMap[method] || method
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = placeholderImage
}

// 生命周期
onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.status-filter {
  margin-bottom: 20px;
}

.orders-list {
  margin-bottom: 30px;
}

.order-card {
  margin-bottom: 20px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.order-number {
  font-weight: 500;
  color: #303133;
}

.order-time {
  font-size: 12px;
  color: #909399;
}

.order-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.product-info {
  display: flex;
  gap: 15px;
  flex: 1;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-details h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.product-price {
  margin: 0 0 5px 0;
  font-weight: 500;
  color: #f56c6c;
}

.quantity {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.order-total {
  text-align: right;
}

.total-amount,
.payment-method {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.label {
  color: #606266;
  font-size: 14px;
}

.amount {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.method {
  color: #303133;
  font-weight: 500;
}

.order-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination {
  display: flex;
  justify-content: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.delivery-content {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
}

.delivery-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
  font-size: 14px;
  color: #303133;
}

@media (max-width: 768px) {
  .orders {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .order-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .order-total {
    text-align: left;
    width: 100%;
  }

  .total-amount,
  .payment-method {
    justify-content: flex-start;
  }

  .order-actions {
    justify-content: center;
  }
}
</style>

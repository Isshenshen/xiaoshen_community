<template>
  <div class="admin-orders">
    <div class="page-header">
      <h2>订单管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="exportOrders">
          导出订单
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in orderStats" :key="stat.key">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="订单号">
          <el-input
            v-model="filterForm.order_number"
            placeholder="输入订单号"
            clearable
          />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input
            v-model="filterForm.username"
            placeholder="输入用户名"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已发货" value="delivered" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card>
      <el-table
        :data="orders"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="order_number" label="订单号" width="180" fixed />
        <el-table-column prop="user.username" label="用户名" width="120" />
        <el-table-column prop="product_name" label="商品名称" min-width="200" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="total_amount" label="订单金额" width="120">
          <template #default="{ row }">
            ¥{{ row.total_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentMethodText(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="支付时间" width="180">
          <template #default="{ row }">
            {{ row.paid_at ? formatTime(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrder(row)">查看</el-button>
            <el-button
              v-if="row.status === 'paid'"
              size="small"
              type="success"
              @click="deliverOrder(row)"
            >
              发货
            </el-button>
            <el-button
              v-if="row.status === 'delivered'"
              size="small"
              type="warning"
              @click="refundOrder(row)"
            >
              退款
            </el-button>
            <el-button size="small" @click="editOrder(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="showOrderDialog"
      title="订单详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedOrder" class="order-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">
            {{ selectedOrder.order_number }}
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            {{ selectedOrder.user?.username }}
          </el-descriptions-item>
          <el-descriptions-item label="商品名称">
            {{ selectedOrder.product_name }}
          </el-descriptions-item>
          <el-descriptions-item label="商品单价">
            ¥{{ selectedOrder.product_price }}
          </el-descriptions-item>
          <el-descriptions-item label="购买数量">
            {{ selectedOrder.quantity }}
          </el-descriptions-item>
          <el-descriptions-item label="订单总价">
            ¥{{ selectedOrder.total_amount }}
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">
            {{ getPaymentMethodText(selectedOrder.payment_method) }}
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(selectedOrder.status)">
              {{ getStatusText(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="下单时间">
            {{ formatTime(selectedOrder.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="支付时间">
            {{ selectedOrder.paid_at ? formatTime(selectedOrder.paid_at) : '未支付' }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedOrder.user_note" class="order-notes">
          <h4>买家留言</h4>
          <p>{{ selectedOrder.user_note }}</p>
        </div>

        <div v-if="selectedOrder.admin_note" class="order-notes">
          <h4>管理员备注</h4>
          <p>{{ selectedOrder.admin_note }}</p>
        </div>

        <div v-if="selectedOrder.delivery_content" class="delivery-content">
          <h4>发货内容</h4>
          <pre>{{ selectedOrder.delivery_content }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="showOrderDialog = false">关闭</el-button>
        <el-button
          v-if="selectedOrder?.status === 'paid'"
          type="primary"
          @click="deliverOrder(selectedOrder)"
        >
          立即发货
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑订单对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑订单"
      width="600px"
    >
      <el-form
        v-if="selectedOrder"
        :model="editForm"
        label-width="100px"
      >
        <el-form-item label="订单状态">
          <el-select v-model="editForm.status">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已发货" value="delivered" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>

        <el-form-item label="管理员备注">
          <el-input
            v-model="editForm.admin_note"
            type="textarea"
            :rows="3"
            placeholder="输入管理员备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="submitEditForm" :loading="editing">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 订单接口
interface Order {
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
  user_note?: string
  admin_note?: string
  created_at: string
  paid_at?: string
  user?: {
    username: string
  }
}

// 模拟订单数据
const orders = ref<Order[]>([
  {
    id: 1,
    order_number: 'ORD20241201001',
    user_id: 1,
    product_id: 1,
    product_name: 'Vue3 + FastAPI全栈博客系统',
    product_price: 99.00,
    quantity: 1,
    total_amount: 99.00,
    payment_method: 'balance',
    status: 'paid',
    created_at: '2024-12-01T10:00:00Z',
    paid_at: '2024-12-01T10:05:00Z',
    user: { username: 'user1' },
  },
  {
    id: 2,
    order_number: 'ORD20241201002',
    user_id: 2,
    product_id: 2,
    product_name: 'React Native电商App',
    product_price: 199.00,
    quantity: 1,
    total_amount: 199.00,
    payment_method: 'alipay',
    status: 'delivered',
    created_at: '2024-12-01T11:00:00Z',
    paid_at: '2024-12-01T11:05:00Z',
    delivery_content: '源码下载链接: https://download.example.com/project/react-ecommerce.zip',
    user: { username: 'user2' },
  },
])

const orderStats = ref([
  { key: 'total', label: '总订单', value: '156' },
  { key: 'pending', label: '待支付', value: '12' },
  { key: 'paid', label: '已支付', value: '89' },
  { key: 'delivered', label: '已发货', value: '55' },
])

const total = ref(orders.value.length)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showOrderDialog = ref(false)
const showEditDialog = ref(false)
const editing = ref(false)
const selectedOrder = ref<Order | null>(null)

// 表单数据
const filterForm = reactive({
  order_number: '',
  username: '',
  status: '',
})

const dateRange = ref('')
const editForm = reactive({
  status: '',
  admin_note: '',
})

// 方法
const loadOrders = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取订单列表
    // 这里使用模拟数据和筛选
    let filteredOrders = orders.value

    if (filterForm.order_number) {
      filteredOrders = filteredOrders.filter(order =>
        order.order_number.includes(filterForm.order_number)
      )
    }

    if (filterForm.username) {
      filteredOrders = filteredOrders.filter(order =>
        order.user?.username.includes(filterForm.username)
      )
    }

    if (filterForm.status) {
      filteredOrders = filteredOrders.filter(order =>
        order.status === filterForm.status
      )
    }

    total.value = filteredOrders.length
  } catch (error) {
    ElMessage.error('加载订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  loadOrders()
}

const resetFilter = () => {
  Object.assign(filterForm, {
    order_number: '',
    username: '',
    status: '',
  })
  dateRange.value = ''
  handleFilter()
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

const handleSelectionChange = (selection: Order[]) => {
  // 处理选中项变化
}

const viewOrder = (order: Order) => {
  selectedOrder.value = order
  showOrderDialog.value = true
}

const deliverOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      '确定要发货吗？发货后将无法取消订单。',
      '确认发货',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API发货
    order.status = 'delivered'
    order.delivery_content = `感谢购买！您的源码项目已准备就绪。

项目信息：
- 商品名称: ${order.product_name}
- 购买数量: ${order.quantity}
- 订单号: ${order.order_number}

下载链接：
https://download.example.com/project/${order.product_id}.zip

解压密码: codehub2024

技术支持QQ: 123456789`

    ElMessage.success('订单已发货')
    showOrderDialog.value = false

  } catch {
    // 用户取消
  }
}

const refundOrder = async (order: Order) => {
  try {
    await ElMessageBox.confirm(
      '确定要退款吗？退款后订单状态将变更为"已退款"。',
      '确认退款',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API退款
    order.status = 'refunded'
    ElMessage.success('退款成功')

  } catch {
    // 用户取消
  }
}

const editOrder = (order: Order) => {
  selectedOrder.value = order
  Object.assign(editForm, {
    status: order.status,
    admin_note: order.admin_note || '',
  })
  showEditDialog.value = true
}

const submitEditForm = async () => {
  if (!selectedOrder.value) return

  editing.value = true
  try {
    // TODO: 调用API更新订单
    Object.assign(selectedOrder.value, editForm)
    ElMessage.success('订单更新成功')
    showEditDialog.value = false
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    editing.value = false
  }
}

const exportOrders = () => {
  // TODO: 实现订单导出功能
  ElMessage.info('导出功能开发中...')
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

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.admin-orders {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px;
}

.order-details {
  max-height: 600px;
  overflow-y: auto;
}

.order-notes,
.delivery-content {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.order-notes h4,
.delivery-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.delivery-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #303133;
}

@media (max-width: 768px) {
  .admin-orders {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .filter-form {
    flex-direction: column;
  }

  .stats-cards .el-col {
    margin-bottom: 15px;
  }
}
</style>

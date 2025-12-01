<template>
  <div class="recharge">
    <el-card class="recharge-card">
      <template #header>
        <div class="card-header">
          <h2>余额充值</h2>
          <div class="balance-info">
            当前余额: <span class="balance">¥{{ user?.balance?.toFixed(2) }}</span>
          </div>
        </div>
      </template>

      <div class="recharge-content">
        <!-- 充值金额选择 -->
        <div class="amount-selection">
          <h3>选择充值金额</h3>
          <div class="amount-options">
            <el-button
              v-for="amount in presetAmounts"
              :key="amount"
              :type="selectedAmount === amount ? 'primary' : 'default'"
              size="large"
              @click="selectAmount(amount)"
            >
              ¥{{ amount }}
            </el-button>
          </div>

          <div class="custom-amount">
            <el-input
              v-model="customAmount"
              placeholder="输入自定义金额"
              type="number"
              :min="1"
              :max="10000"
              size="large"
              @input="handleCustomAmount"
            >
              <template #prefix>¥</template>
            </el-input>
          </div>
        </div>

        <!-- 支付方式选择 -->
        <div class="payment-methods">
          <h3>选择支付方式</h3>
          <div class="method-options">
            <div
              v-for="method in paymentMethods"
              :key="method.value"
              class="method-card"
              :class="{ active: selectedMethod === method.value }"
              @click="selectMethod(method.value)"
            >
              <div class="method-icon">
                <el-icon :size="32">
                  <component :is="method.icon" />
                </el-icon>
              </div>
              <div class="method-info">
                <div class="method-name">{{ method.name }}</div>
                <div class="method-desc">{{ method.description }}</div>
              </div>
              <div class="method-check">
                <el-icon v-if="selectedMethod === method.value" :size="20" color="#409eff">
                  <Check />
                </el-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- 充值按钮 -->
        <div class="recharge-action">
          <div class="amount-summary">
            <span>充值金额: </span>
            <span class="amount">¥{{ currentAmount }}</span>
          </div>
          <el-button
            type="primary"
            size="large"
            :disabled="!canRecharge"
            :loading="recharging"
            @click="handleRecharge"
          >
            立即充值
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 充值记录 -->
    <el-card class="recharge-history">
      <template #header>
        <span>充值记录</span>
      </template>

      <el-table :data="rechargeRecords" style="width: 100%">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="120">
          <template #default="{ row }">
            {{ getPaymentMethodName(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="rechargeRecords.length === 0" class="empty-records">
        <el-empty description="暂无充值记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Money, CreditCard, WechatPay, Alipay, Check } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 数据
const selectedAmount = ref(0)
const customAmount = ref('')
const selectedMethod = ref('')
const recharging = ref(false)

// 预设金额
const presetAmounts = [10, 50, 100, 200, 500, 1000]

// 支付方式
const paymentMethods = [
  {
    value: 'alipay',
    name: '支付宝',
    description: '推荐使用支付宝支付',
    icon: Alipay,
  },
  {
    value: 'wechat',
    name: '微信支付',
    description: '推荐使用微信支付',
    icon: WechatPay,
  },
  {
    value: 'balance',
    name: '余额支付',
    description: '使用现有余额充值',
    icon: Money,
  },
]

// 模拟充值记录
const rechargeRecords = ref([
  // 这里应该从API获取真实数据
])

// 计算属性
const user = computed(() => authStore.user)
const currentAmount = computed(() => {
  return selectedAmount.value || parseFloat(customAmount.value) || 0
})
const canRecharge = computed(() => {
  return currentAmount.value > 0 && selectedMethod.value && !recharging.value
})

// 方法
const selectAmount = (amount: number) => {
  selectedAmount.value = amount
  customAmount.value = ''
}

const handleCustomAmount = () => {
  selectedAmount.value = 0
}

const selectMethod = (method: string) => {
  selectedMethod.value = method
}

const handleRecharge = async () => {
  if (!canRecharge.value) return

  try {
    await ElMessageBox.confirm(
      `确认充值 ¥${currentAmount.value}？\n支付方式: ${getPaymentMethodName(selectedMethod.value)}`,
      '确认充值',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    recharging.value = true

    // TODO: 调用充值API
    // 这里模拟充值过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 更新用户余额（实际应该从API响应中获取）
    if (authStore.user) {
      authStore.user.balance += currentAmount.value
    }

    ElMessage.success('充值成功！')

    // 重置表单
    selectedAmount.value = 0
    customAmount.value = ''
    selectedMethod.value = ''

  } catch (error) {
    // 用户取消操作
  } finally {
    recharging.value = false
  }
}

const getPaymentMethodName = (method: string) => {
  const methodMap: Record<string, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    balance: '余额支付',
  }
  return methodMap[method] || method
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    pending: 'warning',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    success: '成功',
    failed: '失败',
    pending: '处理中',
  }
  return statusMap[status] || status
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.recharge {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.recharge-card {
  margin-bottom: 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-header h2 {
  margin: 0;
}

.balance-info {
  color: #606266;
  font-size: 14px;
}

.balance {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.recharge-content {
  padding: 20px 0;
}

.amount-selection,
.payment-methods {
  margin-bottom: 40px;
}

.amount-selection h3,
.payment-methods h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
}

.amount-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.custom-amount {
  max-width: 200px;
}

.method-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.method-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.method-card:hover,
.method-card.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.method-icon {
  margin-right: 15px;
  color: #409eff;
}

.method-info {
  flex: 1;
}

.method-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.method-desc {
  font-size: 14px;
  color: #909399;
}

.method-check {
  margin-left: 15px;
}

.recharge-action {
  text-align: center;
  padding: 30px 0;
  border-top: 1px solid #ebeef5;
}

.amount-summary {
  margin-bottom: 20px;
  font-size: 16px;
  color: #606266;
}

.amount {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
}

.recharge-history {
  margin-bottom: 40px;
}

.empty-records {
  text-align: center;
  padding: 40px;
}

@media (max-width: 768px) {
  .recharge {
    padding: 20px 10px;
  }

  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .amount-options {
    grid-template-columns: repeat(3, 1fr);
  }

  .method-card {
    padding: 15px;
  }

  .method-info {
    flex: 1;
    min-width: 0;
  }
}
</style>

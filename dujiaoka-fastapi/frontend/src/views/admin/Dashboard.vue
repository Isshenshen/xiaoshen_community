<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h2>后台管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/')">
          返回前台
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in stats" :key="stat.key">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon :size="32">
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 订单趋势图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>订单趋势</span>
          </template>
          <div class="chart-container" ref="orderChartRef"></div>
        </el-card>
      </el-col>

      <!-- 收入趋势图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>收入趋势</span>
          </template>
          <div class="chart-container" ref="revenueChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="quick-actions">
      <template #header>
        <span>快速操作</span>
      </template>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/admin/products')" icon="Plus">
          添加商品
        </el-button>
        <el-button type="success" @click="$router.push('/admin/orders')" icon="List">
          管理订单
        </el-button>
        <el-button type="warning" @click="$router.push('/admin/order-templates')" icon="DocumentAdd">
          创建订单模板
        </el-button>
        <el-button type="info" @click="$router.push('/admin/users')" icon="User">
          用户管理
        </el-button>
      </div>
    </el-card>

    <!-- 销售排行 -->
    <el-card class="sales-card">
      <template #header>
        <span>商品销售排行</span>
      </template>
      <el-table :data="salesData" style="width: 100%">
        <el-table-column prop="product" label="商品名称" />
        <el-table-column prop="quantity" label="销量" width="120" />
        <el-table-column prop="revenue" label="销售额" width="120">
          <template #default="{ row }">
            ¥{{ row.revenue }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  ShoppingCart,
  Money,
  Check,
  TrendingUp,
  Dollar,
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const orderChartRef = ref()
const revenueChartRef = ref()

// 统计数据
const stats = ref([
  {
    key: 'total_users',
    label: '总用户数',
    value: '0',
    icon: User,
  },
  {
    key: 'total_orders',
    label: '总订单数',
    value: '0',
    icon: ShoppingCart,
  },
  {
    key: 'total_revenue',
    label: '总收入',
    value: '¥0.00',
    icon: Money,
  },
  {
    key: 'success_rate',
    label: '成功率',
    value: '0%',
    icon: Check,
  },
])

// 销售数据
const salesData = ref([
  // 这里应该从API获取数据
])

// 图表数据
const orderChartData = ref([])
const revenueChartData = ref([])

// API调用方法
const fetchDashboardStats = async () => {
  try {
    const response = await fetch('/api/v1/admin/dashboard/stats', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
  return null
}

const fetchDashboardCharts = async () => {
  try {
    const response = await fetch('/api/v1/admin/dashboard/charts?days=7', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.error('获取图表数据失败:', error)
  }
  return null
}

// 方法
const loadDashboardData = async () => {
  try {
    // 获取统计数据
    const statsData = await fetchDashboardStats()
    if (statsData) {
      stats.value = [
        {
          key: 'total_users',
          label: '总用户数',
          value: statsData.total_users?.toLocaleString() || '0',
          icon: User,
        },
        {
          key: 'total_orders',
          label: '总订单数',
          value: statsData.total_orders?.toLocaleString() || '0',
          icon: ShoppingCart,
        },
        {
          key: 'total_revenue',
          label: '总收入',
          value: `¥${(statsData.total_revenue || 0).toLocaleString()}`,
          icon: Money,
        },
        {
          key: 'success_rate',
          label: '成功率',
          value: '98.5%', // 这里可以根据实际数据计算
          icon: Check,
        },
      ]
    }

    // 获取图表数据
    const chartsData = await fetchDashboardCharts()
    if (chartsData) {
      // 处理订单图表数据
      orderChartData.value = chartsData.order_chart?.map(item => ({
        date: item.date,
        orders: item.orders
      })) || []

      // 处理收入图表数据
      revenueChartData.value = chartsData.revenue_chart?.map(item => ({
        date: item.date,
        revenue: item.revenue
      })) || []

      // 处理销售排行数据
      salesData.value = chartsData.sales_chart?.map(item => ({
        product: item.product,
        quantity: item.quantity,
        revenue: item.revenue
      })) || []
    }

    // 如果API调用失败，使用模拟数据作为后备
    if (!statsData) {
      stats.value = [
        {
          key: 'total_users',
          label: '总用户数',
          value: '加载中...',
          icon: User,
        },
        {
          key: 'total_orders',
          label: '总订单数',
          value: '加载中...',
          icon: ShoppingCart,
        },
        {
          key: 'total_revenue',
          label: '总收入',
          value: '¥0.00',
          icon: Money,
        },
        {
          key: 'success_rate',
          label: '成功率',
          value: '0%',
          icon: Check,
        },
      ]
    }

    if (!chartsData) {
      // 使用默认模拟数据
      salesData.value = [
        { product: '数据加载中...', quantity: 0, revenue: 0 },
      ]
      orderChartData.value = []
      revenueChartData.value = []
    }

    // 渲染图表
    renderCharts()

  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Dashboard error:', error)
  }
}

const renderCharts = () => {
  // 订单趋势图
  if (orderChartRef.value) {
    const orderChart = echarts.init(orderChartRef.value)
    const orderOption = {
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: orderChartData.value.map(item => item.date),
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: '订单数',
          type: 'line',
          data: orderChartData.value.map(item => item.orders),
          smooth: true,
          itemStyle: { color: '#409eff' },
        },
      ],
    }
    orderChart.setOption(orderOption)
  }

  // 收入趋势图
  if (revenueChartRef.value) {
    const revenueChart = echarts.init(revenueChartRef.value)
    const revenueOption = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          return `收入: ¥${params[0].value}`
        },
      },
      xAxis: {
        type: 'category',
        data: revenueChartData.value.map(item => item.date),
      },
      yAxis: {
        type: 'value',
      },
      series: [
        {
          name: '收入',
          type: 'bar',
          data: revenueChartData.value.map(item => item.revenue),
          itemStyle: { color: '#67c23a' },
        },
      ],
    }
    revenueChart.setOption(revenueOption)
  }
}

// 生命周期
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.dashboard-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.stat-icon {
  color: #409eff;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.sales-card {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 10px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .stat-content {
    flex-direction: column;
    gap: 10px;
  }

  .stat-value {
    font-size: 20px;
  }

  .chart-container {
    height: 250px;
  }
}
</style>

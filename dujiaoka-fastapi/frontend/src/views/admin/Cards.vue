<template>
  <div class="admin-cards">
    <div class="page-header">
      <h2>卡密管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          添加卡密
        </el-button>
        <el-button type="success" @click="showBatchImportDialog = true">
          批量导入
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="项目ID">
          <el-input
            v-model="filterForm.product_id"
            placeholder="输入项目ID"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="未使用" value="unused" />
            <el-option label="已使用" value="used" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 卡密列表 -->
    <el-card>
      <el-table
        :data="cards"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="product_id" label="项目ID" width="100" />
        <el-table-column label="卡密内容" min-width="200">
          <template #default="{ row }">
            <span class="card-content">{{ maskCardContent(row.encrypted_content) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="used_by" label="使用者ID" width="120" />
        <el-table-column prop="used_at" label="使用时间" width="180">
          <template #default="{ row }">
            {{ row.used_at ? formatTime(row.used_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" width="180">
          <template #default="{ row }">
            {{ row.expires_at ? formatTime(row.expires_at) : '永久' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewCard(row)">查看</el-button>
            <el-button
              v-if="row.status === 'unused'"
              size="small"
              type="warning"
              @click="lockCard(row)"
            >
              锁定
            </el-button>
            <el-button
              v-if="row.status === 'locked'"
              size="small"
              type="success"
              @click="unlockCard(row)"
            >
              解锁
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteCard(row)"
            >
              删除
            </el-button>
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

    <!-- 添加卡密对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="添加卡密"
      width="600px"
    >
      <el-form
        ref="cardFormRef"
        :model="cardForm"
        :rules="cardRules"
        label-width="100px"
      >
        <el-form-item label="项目ID" prop="product_id">
          <el-input-number
            v-model="cardForm.product_id"
            :min="1"
            placeholder="输入项目ID"
          />
        </el-form-item>

        <el-form-item label="卡密内容" prop="encrypted_content">
          <el-input
            v-model="cardForm.encrypted_content"
            type="textarea"
            :rows="4"
            placeholder="输入卡密内容"
          />
        </el-form-item>

        <el-form-item label="过期时间">
          <el-date-picker
            v-model="cardForm.expires_at"
            type="datetime"
            placeholder="选择过期时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCardForm" :loading="submitting">
          添加
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showBatchImportDialog"
      title="批量导入卡密"
      width="600px"
    >
      <el-form
        ref="batchFormRef"
        :model="batchForm"
        :rules="batchRules"
        label-width="100px"
      >
        <el-form-item label="项目ID" prop="product_id">
          <el-input-number
            v-model="batchForm.product_id"
            :min="1"
            placeholder="输入项目ID"
          />
        </el-form-item>

        <el-form-item label="卡密列表" prop="card_contents">
          <el-input
            v-model="batchForm.card_contents"
            type="textarea"
            :rows="8"
            placeholder="每行一个卡密内容"
          />
          <div class="form-tip">
            提示：每行输入一个卡密内容，支持批量导入
          </div>
        </el-form-item>

        <el-form-item label="过期时间">
          <el-date-picker
            v-model="batchForm.expires_at"
            type="datetime"
            placeholder="选择过期时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showBatchImportDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBatchForm" :loading="batchSubmitting">
          批量导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看卡密对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="卡密详情"
      width="600px"
    >
      <div class="card-details">
        <div class="detail-item">
          <span class="label">卡密ID:</span>
          <span class="value">{{ selectedCard?.id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">项目ID:</span>
          <span class="value">{{ selectedCard?.product_id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">状态:</span>
          <el-tag :type="getStatusType(selectedCard?.status)">
            {{ getStatusText(selectedCard?.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="label">卡密内容:</span>
          <div class="card-content-full">
            <pre>{{ selectedCard?.encrypted_content }}</pre>
          </div>
        </div>
        <div class="detail-item" v-if="selectedCard?.used_by">
          <span class="label">使用者:</span>
          <span class="value">{{ selectedCard?.used_by }}</span>
        </div>
        <div class="detail-item" v-if="selectedCard?.used_at">
          <span class="label">使用时间:</span>
          <span class="value">{{ formatTime(selectedCard?.used_at) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">过期时间:</span>
          <span class="value">{{ selectedCard?.expires_at ? formatTime(selectedCard?.expires_at) : '永久' }}</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
        <el-button type="primary" @click="copyCardContent">
          复制卡密
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 卡密接口
interface Card {
  id: number
  product_id: number
  encrypted_content: string
  status: string
  used_by?: number
  used_at?: string
  expires_at?: string
  created_at: string
}

// 模拟卡密数据
const cards = ref<Card[]>([
  {
    id: 1,
    product_id: 1,
    encrypted_content: "CARD-SECRET-001-ABCDEFGH",
    status: "unused",
    created_at: "2024-12-01T10:00:00Z",
  },
  {
    id: 2,
    product_id: 1,
    encrypted_content: "CARD-SECRET-002-IJKLMNOP",
    status: "used",
    used_by: 123,
    used_at: "2024-12-01T11:00:00Z",
    created_at: "2024-12-01T10:00:00Z",
  },
  {
    id: 3,
    product_id: 2,
    encrypted_content: "CARD-SECRET-003-QRSTUVWX",
    status: "locked",
    created_at: "2024-12-01T10:00:00Z",
  },
])

const total = ref(cards.value.length)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showCreateDialog = ref(false)
const showBatchImportDialog = ref(false)
const showViewDialog = ref(false)
const submitting = ref(false)
const batchSubmitting = ref(false)
const selectedCard = ref<Card | null>(null)

// 表单数据
const filterForm = reactive({
  product_id: '',
  status: '',
})

const cardForm = reactive({
  product_id: 1,
  encrypted_content: '',
  expires_at: '',
})

const batchForm = reactive({
  product_id: 1,
  card_contents: '',
  expires_at: '',
})

// 表单验证规则
const cardRules = {
  product_id: [
    { required: true, message: '请输入项目ID', trigger: 'blur' },
  ],
  encrypted_content: [
    { required: true, message: '请输入卡密内容', trigger: 'blur' },
  ],
}

const batchRules = {
  product_id: [
    { required: true, message: '请输入项目ID', trigger: 'blur' },
  ],
  card_contents: [
    { required: true, message: '请输入卡密内容', trigger: 'blur' },
  ],
}

// 方法
const loadCards = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取卡密列表
    // 这里使用模拟数据
    // 应用筛选
    let filteredCards = cards.value
    if (filterForm.product_id) {
      filteredCards = filteredCards.filter(card =>
        card.product_id.toString().includes(filterForm.product_id)
      )
    }
    if (filterForm.status) {
      filteredCards = filteredCards.filter(card => card.status === filterForm.status)
    }

    total.value = filteredCards.length
  } catch (error) {
    ElMessage.error('加载卡密列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  loadCards()
}

const resetFilter = () => {
  Object.assign(filterForm, {
    product_id: '',
    status: '',
  })
  handleFilter()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadCards()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadCards()
}

const handleSelectionChange = (selection: Card[]) => {
  // 处理选中项变化
}

const viewCard = (card: Card) => {
  selectedCard.value = card
  showViewDialog.value = true
}

const lockCard = async (card: Card) => {
  try {
    await ElMessageBox.confirm(
      '确定要锁定此卡密吗？',
      '确认锁定',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API锁定卡密
    card.status = 'locked'
    ElMessage.success('卡密已锁定')

  } catch {
    // 用户取消
  }
}

const unlockCard = async (card: Card) => {
  try {
    await ElMessageBox.confirm(
      '确定要解锁此卡密吗？',
      '确认解锁',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API解锁卡密
    card.status = 'unused'
    ElMessage.success('卡密已解锁')

  } catch {
    // 用户取消
  }
}

const deleteCard = async (card: Card) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此卡密吗？此操作不可恢复！',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error',
      }
    )

    // TODO: 调用API删除卡密
    const index = cards.value.findIndex(c => c.id === card.id)
    if (index > -1) {
      cards.value.splice(index, 1)
      total.value--
    }
    ElMessage.success('卡密已删除')

  } catch {
    // 用户取消
  }
}

const submitCardForm = async () => {
  // TODO: 实现卡密创建逻辑
  ElMessage.success('卡密创建成功')
  showCreateDialog.value = false
  resetCardForm()
  loadCards()
}

const submitBatchForm = async () => {
  // TODO: 实现批量导入逻辑
  ElMessage.success('批量导入成功')
  showBatchImportDialog.value = false
  resetBatchForm()
  loadCards()
}

const copyCardContent = async () => {
  if (!selectedCard?.encrypted_content) return

  try {
    await navigator.clipboard.writeText(selectedCard.encrypted_content)
    ElMessage.success('卡密已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const resetCardForm = () => {
  Object.assign(cardForm, {
    product_id: 1,
    encrypted_content: '',
    expires_at: '',
  })
}

const resetBatchForm = () => {
  Object.assign(batchForm, {
    product_id: 1,
    card_contents: '',
    expires_at: '',
  })
}

const maskCardContent = (content: string) => {
  // 隐藏卡密内容，只显示前8位和后4位
  if (content.length <= 12) return content
  return content.substring(0, 8) + '****' + content.substring(content.length - 4)
}

const getStatusType = (status: string) => {
  const statusMap = {
    unused: 'success',
    used: 'info',
    locked: 'warning',
    expired: 'danger',
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    unused: '未使用',
    used: '已使用',
    locked: '已锁定',
    expired: '已过期',
  }
  return statusMap[status] || status
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadCards()
})
</script>

<style scoped>
.admin-cards {
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

.card-content {
  font-family: monospace;
  font-size: 12px;
}

.card-details {
  padding: 20px 0;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.label {
  width: 100px;
  color: #909399;
  font-weight: 500;
  flex-shrink: 0;
}

.value {
  color: #303133;
  flex: 1;
}

.card-content-full {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  width: 100%;
}

.card-content-full pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
  font-size: 14px;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

@media (max-width: 768px) {
  .admin-cards {
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

  .detail-item {
    flex-direction: column;
    gap: 5px;
  }

  .label {
    width: auto;
  }
}
</style>

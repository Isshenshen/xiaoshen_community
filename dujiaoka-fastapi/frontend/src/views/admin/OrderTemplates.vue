<template>
  <div class="admin-order-templates">
    <div class="page-header">
      <h2>订单模板管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          创建订单模板
        </el-button>
      </div>
    </div>

    <!-- 模板列表 -->
    <el-card>
      <el-table
        :data="orderTemplates"
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="模板标题" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyType(row.difficulty)">
              {{ row.difficulty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewTemplate(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editTemplate(row)">编辑</el-button>
            <el-button
              size="small"
              type="warning"
              @click="toggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteTemplate(row)"
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

    <!-- 创建/编辑模板对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="templateFormRef"
        :model="templateForm"
        :rules="templateRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板标题" prop="title">
              <el-input v-model="templateForm.title" placeholder="输入模板标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number
                v-model="templateForm.price"
                :min="0"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="templateForm.category" placeholder="选择分类" style="width: 100%">
                <el-option label="Web开发" value="web" />
                <el-option label="移动开发" value="mobile" />
                <el-option label="工具软件" value="tool" />
                <el-option label="API服务" value="api" />
                <el-option label="数据分析" value="data" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级">
              <el-select v-model="templateForm.difficulty" placeholder="选择难度" style="width: 100%">
                <el-option label="入门" value="入门" />
                <el-option label="中级" value="中级" />
                <el-option label="高级" value="高级" />
                <el-option label="专家" value="专家" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述项目功能和技术特点"
          />
        </el-form-item>

        <el-form-item label="技术栈">
          <el-input
            v-model="templateForm.tech_stack"
            placeholder="例如: Vue.js, FastAPI, PostgreSQL"
          />
        </el-form-item>

        <el-form-item label="交付内容">
          <el-input
            v-model="templateForm.delivery_content"
            type="textarea"
            :rows="4"
            placeholder="描述购买后将获得的源码和资源"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预计工期(天)">
              <el-input-number
                v-model="templateForm.estimated_days"
                :min="1"
                :max="365"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="支持次数">
              <el-input-number
                v-model="templateForm.support_count"
                :min="0"
                style="width: 100%"
                placeholder="技术支持次数，0表示无限"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="模板封面">
          <el-input
            v-model="templateForm.image_url"
            placeholder="封面图片URL"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="templateForm.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTemplateForm" :loading="submitting">
          {{ editingTemplate ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看模板详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="模板详情"
      width="700px"
    >
      <div v-if="selectedTemplate" class="template-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标题">
            {{ selectedTemplate.title }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">
            ¥{{ selectedTemplate.price }}
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            {{ selectedTemplate.category }}
          </el-descriptions-item>
          <el-descriptions-item label="难度">
            <el-tag :type="getDifficultyType(selectedTemplate.difficulty)">
              {{ selectedTemplate.difficulty }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="技术栈">
            {{ selectedTemplate.tech_stack }}
          </el-descriptions-item>
          <el-descriptions-item label="预计工期">
            {{ selectedTemplate.estimated_days }}天
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedTemplate.is_active ? 'success' : 'danger'">
              {{ selectedTemplate.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(selectedTemplate.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="template-description">
          <h4>项目描述</h4>
          <p>{{ selectedTemplate.description }}</p>
        </div>

        <div class="template-delivery">
          <h4>交付内容</h4>
          <p>{{ selectedTemplate.delivery_content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 订单模板接口
interface OrderTemplate {
  id: number
  title: string
  description: string
  price: number
  category: string
  difficulty: string
  tech_stack?: string
  delivery_content?: string
  estimated_days?: number
  support_count?: number
  image_url?: string
  is_active: boolean
  created_at: string
}

// 模拟订单模板数据
const orderTemplates = ref<OrderTemplate[]>([
  {
    id: 1,
    title: 'Vue3 + FastAPI全栈电商系统',
    description: '完整的电商系统源码，包含前端后台管理、支付集成、订单管理等功能',
    price: 1999.00,
    category: 'web',
    difficulty: '高级',
    tech_stack: 'Vue3, FastAPI, PostgreSQL, Redis',
    delivery_content: '完整源码、部署文档、API文档、数据库脚本、30天技术支持',
    estimated_days: 30,
    support_count: 10,
    image_url: '/project1.jpg',
    is_active: true,
    created_at: '2024-12-01T10:00:00Z',
  },
  {
    id: 2,
    title: 'React Native社交App',
    description: '功能完整的社交应用，包含聊天、朋友圈、动态发布等功能',
    price: 2999.00,
    category: 'mobile',
    difficulty: '专家',
    tech_stack: 'React Native, Node.js, MongoDB, Socket.io',
    delivery_content: 'iOS/Android源码、服务器端代码、数据库设计、部署指南、无限技术支持',
    estimated_days: 45,
    support_count: 0, // 无限
    image_url: '/project2.jpg',
    is_active: true,
    created_at: '2024-12-02T11:00:00Z',
  },
  {
    id: 3,
    title: 'Python数据分析平台',
    description: '企业级数据分析平台，支持多种数据源、图表展示、报告生成',
    price: 3999.00,
    category: 'data',
    difficulty: '专家',
    tech_stack: 'Python, FastAPI, Vue3, PostgreSQL, Pandas',
    delivery_content: '完整系统源码、算法模型、部署脚本、使用文档、60天技术支持',
    estimated_days: 60,
    support_count: 20,
    image_url: '/project3.jpg',
    is_active: false,
    created_at: '2024-12-03T12:00:00Z',
  },
])

const total = ref(orderTemplates.value.length)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const submitting = ref(false)
const editingTemplate = ref<OrderTemplate | null>(null)
const selectedTemplate = ref<OrderTemplate | null>(null)

// 表单数据
const templateForm = reactive({
  title: '',
  description: '',
  price: 0,
  category: '',
  difficulty: '',
  tech_stack: '',
  delivery_content: '',
  estimated_days: 7,
  support_count: 5,
  image_url: '',
  is_active: true,
})

// 表单验证规则
const templateRules = {
  title: [
    { required: true, message: '请输入模板标题', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入项目描述', trigger: 'blur' },
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能小于0', trigger: 'blur' },
  ],
}

// 方法
const loadTemplates = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取订单模板列表
    // 这里使用模拟数据
    total.value = orderTemplates.value.length
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadTemplates()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadTemplates()
}

const viewTemplate = (template: OrderTemplate) => {
  selectedTemplate.value = template
  showViewDialog.value = true
}

const editTemplate = (template: OrderTemplate) => {
  editingTemplate.value = template
  Object.assign(templateForm, {
    title: template.title,
    description: template.description,
    price: template.price,
    category: template.category,
    difficulty: template.difficulty,
    tech_stack: template.tech_stack || '',
    delivery_content: template.delivery_content || '',
    estimated_days: template.estimated_days || 7,
    support_count: template.support_count || 5,
    image_url: template.image_url || '',
    is_active: template.is_active,
  })
  showCreateDialog.value = true
}

const toggleStatus = async (template: OrderTemplate) => {
  const action = template.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}模板 "${template.title}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // TODO: 调用API更新模板状态
    template.is_active = !template.is_active
    ElMessage.success(`${action}成功`)

  } catch {
    // 用户取消
  }
}

const deleteTemplate = async (template: OrderTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.title}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error',
      }
    )

    // TODO: 调用API删除模板
    const index = orderTemplates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      orderTemplates.value.splice(index, 1)
      total.value--
    }
    ElMessage.success('删除成功')

  } catch {
    // 用户取消
  }
}

const submitTemplateForm = async () => {
  // TODO: 实现模板创建和更新逻辑
  ElMessage.success(editingTemplate.value ? '模板更新成功' : '模板创建成功')
  showCreateDialog.value = false
  resetTemplateForm()
  loadTemplates()
}

const resetTemplateForm = () => {
  editingTemplate.value = null
  Object.assign(templateForm, {
    title: '',
    description: '',
    price: 0,
    category: '',
    difficulty: '',
    tech_stack: '',
    delivery_content: '',
    estimated_days: 7,
    support_count: 5,
    image_url: '',
    is_active: true,
  })
}

const getDifficultyType = (difficulty: string) => {
  const typeMap = {
    '入门': 'success',
    '中级': 'warning',
    '高级': 'danger',
    '专家': 'danger',
  }
  return typeMap[difficulty] || 'info'
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 计算属性
const dialogTitle = computed(() => {
  return editingTemplate.value ? '编辑订单模板' : '创建订单模板'
})

// 生命周期
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.admin-order-templates {
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

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px;
}

.template-details {
  padding: 20px 0;
}

.template-description,
.template-delivery {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.template-description h4,
.template-delivery h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

@media (max-width: 768px) {
  .admin-order-templates {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
}
</style>

<template>
  <div class="admin-products">
    <div class="page-header">
      <h2>商品管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          添加商品
        </el-button>
        <el-button type="success" @click="batchUpdate">
          批量操作
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in productStats" :key="stat.key">
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
        <el-form-item label="商品名称">
          <el-input
            v-model="filterForm.name"
            placeholder="输入商品名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category_id" placeholder="选择分类" clearable>
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="选择状态" clearable>
            <el-option label="上架" :value="true" />
            <el-option label="下架" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="技术栈">
          <el-input
            v-model="filterForm.tech_stack"
            placeholder="输入技术栈"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 商品列表 -->
    <el-card>
      <el-table
        :data="displayProducts"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="{ row }">
            {{ row.stock === -1 ? '无限' : row.stock }}
          </template>
        </el-table-column>
        <el-table-column prop="sold_count" label="已售" width="100" />
        <el-table-column prop="tech_stack" label="技术栈" width="150" />
        <el-table-column prop="project_type" label="项目类型" width="120" />
        <el-table-column prop="difficulty_level" label="难度等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyType(row.difficulty_level)">
              {{ row.difficulty_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editProduct(row)">编辑</el-button>
            <el-button
              size="small"
              type="warning"
              @click="toggleProductStatus(row)"
            >
              {{ row.is_active ? '下架' : '上架' }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteProduct(row)"
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

    <!-- 添加/编辑商品对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="productForm.name" placeholder="输入商品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品价格" prop="price">
              <el-input-number
                v-model="productForm.price"
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
            <el-form-item label="原价">
              <el-input-number
                v-model="productForm.original_price"
                :min="0"
                :precision="2"
                :step="0.01"
                placeholder="可选"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存" prop="stock">
              <el-input-number
                v-model="productForm.stock"
                :min="-1"
                placeholder="-1表示无限库存"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="productForm.category_id" placeholder="选择分类" style="width: 100%">
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目类型">
              <el-select v-model="productForm.project_type" placeholder="选择项目类型" style="width: 100%">
                <el-option label="Web应用" value="web" />
                <el-option label="移动App" value="app" />
                <el-option label="工具软件" value="tool" />
                <el-option label="API服务" value="api" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="难度等级">
              <el-select v-model="productForm.difficulty_level" placeholder="选择难度等级" style="width: 100%">
                <el-option label="入门" value="入门" />
                <el-option label="中级" value="中级" />
                <el-option label="高级" value="高级" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="自动发货">
              <el-radio-group v-model="productForm.auto_delivery">
                <el-radio :value="true">是</el-radio>
                <el-radio :value="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="技术栈">
          <el-input
            v-model="productForm.tech_stack"
            placeholder="例如: Vue.js, FastAPI, PostgreSQL"
          />
        </el-form-item>

        <el-form-item label="项目演示地址">
          <el-input
            v-model="productForm.project_url"
            placeholder="https://demo.example.com"
          />
        </el-form-item>

        <el-form-item label="下载地址">
          <el-input
            v-model="productForm.download_url"
            placeholder="源码下载地址"
          />
        </el-form-item>

        <el-form-item label="商品图片">
          <el-input
            v-model="productForm.image_url"
            placeholder="图片URL"
          />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述商品功能和技术特点"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上架状态">
              <el-radio-group v-model="productForm.is_active">
                <el-radio :value="true">上架</el-radio>
                <el-radio :value="false">下架</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重">
              <el-input-number
                v-model="productForm.sort_order"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitProductForm" :loading="submitting">
          {{ editingProduct ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { productApi } from '@/api/product'

const authStore = useAuthStore()
const productFormRef = ref<FormInstance>()

// 商品接口
interface Product {
  id: number
  name: string
  description?: string
  price: number
  original_price?: number
  category_id?: number
  stock: number
  sold_count: number
  auto_delivery: boolean
  is_active: boolean
  sort_order: number
  image_url?: string
  project_url?: string
  download_url?: string
  tech_stack?: string
  project_type?: string
  difficulty_level?: string
  created_at: string
}

// 分类接口
interface Category {
  id: number
  name: string
}

// 模拟分类数据
const categories = ref<Category[]>([
  { id: 1, name: 'Web开发' },
  { id: 2, name: '移动开发' },
  { id: 3, name: '工具软件' },
  { id: 4, name: 'API服务' },
])

// 模拟商品数据
const products = ref<Product[]>([
  {
    id: 1,
    name: 'Vue3 + FastAPI全栈博客系统',
    description: '功能完整的博客系统，支持文章发布、评论、用户管理等',
    price: 99.00,
    original_price: 199.00,
    category_id: 1,
    stock: -1,
    sold_count: 45,
    auto_delivery: true,
    is_active: true,
    sort_order: 0,
    image_url: '/product1.jpg',
    project_url: 'https://blog-demo.example.com',
    download_url: 'https://download.example.com/blog-system.zip',
    tech_stack: 'Vue3, FastAPI, PostgreSQL',
    project_type: 'web',
    difficulty_level: '中级',
    created_at: '2024-12-01T10:00:00Z',
  },
  {
    id: 2,
    name: 'React Native电商App',
    description: '跨平台电商应用，支持商品展示、购物车、支付等功能',
    price: 199.00,
    category_id: 2,
    stock: 10,
    sold_count: 23,
    auto_delivery: true,
    is_active: true,
    sort_order: 0,
    image_url: '/product2.jpg',
    tech_stack: 'React Native, Node.js, MongoDB',
    project_type: 'app',
    difficulty_level: '高级',
    created_at: '2024-12-01T11:00:00Z',
  },
])

const productStats = ref([
  { key: 'total', label: '总商品', value: '156' },
  { key: 'active', label: '上架商品', value: '142' },
  { key: 'sold', label: '总销量', value: '1,234' },
  { key: 'revenue', label: '总收入', value: '¥45,678' },
])

// 显示的商品列表（来自 API）
const displayProducts = ref<Product[]>([])
const selectedProducts = ref<Product[]>([])

const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const showCreateDialog = ref(false)
const submitting = ref(false)
const editingProduct = ref<Product | null>(null)

// 对话框标题
const dialogTitle = computed(() => editingProduct.value ? '编辑商品' : '添加商品')

// 表单数据
const filterForm = reactive({
  name: '',
  category_id: null,
  is_active: null,
  tech_stack: '',
})

const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  original_price: null,
  category_id: null,
  stock: -1,
  auto_delivery: true,
  is_active: true,
  sort_order: 0,
  image_url: '',
  project_url: '',
  download_url: '',
  tech_stack: '',
  project_type: '',
  difficulty_level: '',
})

// 表单验证规则
const productRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格不能小于0', trigger: 'blur' },
  ],
  stock: [
    { required: true, message: '请输入库存数量', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' },
  ],
}

// 方法
const fetchCategories = async () => {
  try {
    const { data } = await productApi.getCategories()
    categories.value = data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const { data } = await productApi.getProducts({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      category_id: filterForm.category_id || undefined,
      search: filterForm.name || undefined,
    })

    displayProducts.value = data.items || []
    total.value = data.total || 0
    
    // 更新统计数据
    updateStats()
  } catch (error: any) {
    console.error('加载商品列表失败:', error)
    ElMessage.error('加载商品列表失败')
    // 如果API调用失败，使用模拟数据作为后备
    displayProducts.value = products.value.slice(0, pageSize.value)
    total.value = products.value.length
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const activeCount = displayProducts.value.filter(p => p.is_active).length
  const totalSold = displayProducts.value.reduce((sum, p) => sum + (p.sold_count || 0), 0)
  const totalRevenue = displayProducts.value.reduce((sum, p) => sum + (p.price * (p.sold_count || 0)), 0)
  
  productStats.value = [
    { key: 'total', label: '总商品', value: total.value.toString() },
    { key: 'active', label: '上架商品', value: activeCount.toString() },
    { key: 'sold', label: '总销量', value: totalSold.toLocaleString() },
    { key: 'revenue', label: '总收入', value: `¥${totalRevenue.toLocaleString()}` },
  ]
}

const handleFilter = () => {
  currentPage.value = 1
  loadProducts()
}

const resetFilter = () => {
  Object.assign(filterForm, {
    name: '',
    category_id: null,
    is_active: null,
    tech_stack: '',
  })
  handleFilter()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadProducts()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadProducts()
}

const handleSelectionChange = (selection: Product[]) => {
  selectedProducts.value = selection
}

const editProduct = (product: Product) => {
  editingProduct.value = product
  Object.assign(productForm, {
    name: product.name,
    description: product.description,
    price: product.price,
    original_price: product.original_price,
    category_id: product.category_id,
    stock: product.stock,
    auto_delivery: product.auto_delivery,
    is_active: product.is_active,
    sort_order: product.sort_order,
    image_url: product.image_url || '',
    project_url: product.project_url || '',
    download_url: product.download_url || '',
    tech_stack: product.tech_stack || '',
    project_type: product.project_type || '',
    difficulty_level: product.difficulty_level || '',
  })
  showCreateDialog.value = true
}

const toggleProductStatus = async (product: Product) => {
  const action = product.is_active ? '下架' : '上架'
  try {
    await ElMessageBox.confirm(
      `确定要${action}商品 "${product.name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用 API 更新商品状态
    await productApi.updateProduct(product.id, { is_active: !product.is_active })
    product.is_active = !product.is_active
    ElMessage.success(`${action}成功`)

  } catch (error: any) {
    if (error !== 'cancel' && error?.message !== 'cancel') {
      ElMessage.error(`${action}失败: ${error?.response?.data?.detail || error.message}`)
    }
  }
}

const deleteProduct = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除商品 "${product.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error',
      }
    )

    // 调用 API 删除商品
    await productApi.deleteProduct(product.id)
    
    // 从列表中移除
    const index = displayProducts.value.findIndex(p => p.id === product.id)
    if (index > -1) {
      displayProducts.value.splice(index, 1)
      total.value--
    }
    ElMessage.success('删除成功')

  } catch (error: any) {
    if (error !== 'cancel' && error?.message !== 'cancel') {
      ElMessage.error(`删除失败: ${error?.response?.data?.detail || error.message}`)
    }
  }
}

const submitProductForm = async () => {
  // 表单验证
  if (!productFormRef.value) return
  
  const valid = await productFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  
  try {
    const formData = {
      name: productForm.name,
      description: productForm.description || undefined,
      price: productForm.price,
      original_price: productForm.original_price || undefined,
      category_id: productForm.category_id || undefined,
      stock: productForm.stock,
      auto_delivery: productForm.auto_delivery,
      is_active: productForm.is_active,
      sort_order: productForm.sort_order,
      image_url: productForm.image_url || undefined,
      project_url: productForm.project_url || undefined,
      download_url: productForm.download_url || undefined,
      tech_stack: productForm.tech_stack || undefined,
      project_type: productForm.project_type || undefined,
      difficulty_level: productForm.difficulty_level || undefined,
    }
    
    if (editingProduct.value) {
      // 更新商品
      await productApi.updateProduct(editingProduct.value.id, formData)
      ElMessage.success('商品更新成功')
    } else {
      // 创建商品
      await productApi.createProduct(formData)
      ElMessage.success('商品创建成功')
    }
    
    showCreateDialog.value = false
    resetProductForm()
    loadProducts()
    
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const batchUpdate = async () => {
  if (selectedProducts.value.length === 0) {
    ElMessage.warning('请先选择要操作的商品')
    return
  }
  
  try {
    const action = await ElMessageBox.confirm(
      `已选择 ${selectedProducts.value.length} 个商品，请选择操作：`,
      '批量操作',
      {
        confirmButtonText: '批量上架',
        cancelButtonText: '批量下架',
        distinguishCancelAndClose: true,
        type: 'info',
      }
    ).then(() => 'active').catch((action) => action === 'cancel' ? 'inactive' : null)
    
    if (!action) return
    
    const isActive = action === 'active'
    const actionText = isActive ? '上架' : '下架'
    
    // 批量更新
    loading.value = true
    let successCount = 0
    
    for (const product of selectedProducts.value) {
      try {
        await productApi.updateProduct(product.id, { is_active: isActive })
        product.is_active = isActive
        successCount++
      } catch (error) {
        console.error(`更新商品 ${product.name} 失败:`, error)
      }
    }
    
    ElMessage.success(`批量${actionText}完成，成功 ${successCount}/${selectedProducts.value.length} 个`)
    selectedProducts.value = []
    loadProducts()
    
  } catch (error) {
    // 用户关闭对话框
  } finally {
    loading.value = false
  }
}

const resetProductForm = () => {
  editingProduct.value = null
  Object.assign(productForm, {
    name: '',
    description: '',
    price: 0,
    original_price: null,
    category_id: null,
    stock: -1,
    auto_delivery: true,
    is_active: true,
    sort_order: 0,
    image_url: '',
    project_url: '',
    download_url: '',
    tech_stack: '',
    project_type: '',
    difficulty_level: '',
  })
}

const getDifficultyType = (level: string) => {
  const typeMap = {
    '入门': 'success',
    '中级': 'warning',
    '高级': 'danger',
  }
  return typeMap[level] || 'info'
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  await fetchCategories() // 先加载分类数据
  loadProducts() // 再加载商品数据
})
</script>

<style scoped>
.admin-products {
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

@media (max-width: 768px) {
  .admin-products {
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

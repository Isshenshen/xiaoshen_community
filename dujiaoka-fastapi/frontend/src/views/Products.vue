<template>
  <div class="products">
    <!-- 分类筛选 -->
    <div class="categories">
      <el-button
        :type="selectedCategory === null && !showTemplates ? 'primary' : 'default'"
        @click="selectCategory(null)"
      >
        全部项目
      </el-button>
      <el-button
        v-for="category in categories"
        :key="category.id"
        :type="selectedCategory === category.id ? 'primary' : 'default'"
        @click="selectCategory(category.id)"
      >
        {{ category.name }}
      </el-button>
      <el-button
        :type="showTemplates ? 'primary' : 'default'"
        @click="toggleTemplates"
      >
        定制开发
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索项目源码..."
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon>
            <Search />
          </el-icon>
        </template>
      </el-input>
    </div>

    <!-- 商品列表 -->
    <div class="products-grid">
        <el-row :gutter="20">
          <el-col
            v-for="item in currentItems"
            :key="showTemplates ? `template-${item.id}` : `product-${item.id}`"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
          <el-card
            class="product-card"
            shadow="hover"
            :class="{ 'template-card': showTemplates }"
            @click="showTemplates ? viewTemplate(item) : viewProduct(item.id)"
          >
            <template #header>
              <div class="product-image">
                <img
                  :src="item.image_url || placeholderImage"
                  :alt="showTemplates ? item.title : item.name"
                  @error="handleImageError"
                />
                <div class="product-status" v-if="!item.is_active">
                  <el-tag type="danger">{{ showTemplates ? '已禁用' : '已下架' }}</el-tag>
                </div>
                <div class="template-badge" v-if="showTemplates">
                  <el-tag type="warning">定制开发</el-tag>
                </div>
              </div>
            </template>

            <div class="product-info">
              <h3 class="product-name">
                {{ showTemplates ? item.title : item.name }}
              </h3>
              <p class="product-description">
                {{ (showTemplates ? item.description : item.description || '').length > 60
                  ? (showTemplates ? item.description : item.description || '').substring(0, 60) + '...'
                  : (showTemplates ? item.description : item.description || '') }}
              </p>

              <div class="product-price">
                <span class="current-price">¥{{ item.price }}</span>
                <span class="original-price" v-if="item.original_price && !showTemplates">
                  ¥{{ item.original_price }}
                </span>
              </div>

              <div class="product-meta">
                <div class="meta-row">
                  <el-tag size="small" type="info">
                    {{ showTemplates ? getCategoryName(item.category) : item.category?.name }}
                  </el-tag>
                  <el-tag v-if="showTemplates" size="small" :type="getDifficultyType(item.difficulty)">
                    {{ item.difficulty }}
                  </el-tag>
                </div>
                <div class="meta-stats">
                  <span v-if="!showTemplates && item.sold_count !== undefined">已售: {{ item.sold_count }}</span>
                  <span v-if="showTemplates && item.estimated_days">工期: {{ item.estimated_days }}天</span>
                </div>
              </div>
            </div>

            <template #footer>
              <div class="product-actions">
                <el-button
                  type="primary"
                  size="small"
                  :disabled="!item.is_active || (!showTemplates && item.stock <= 0)"
                  @click.stop="showTemplates ? buyTemplate(item) : buyProduct(item)"
                >
                  {{ (!showTemplates && item.stock <= 0) ? '缺货' : '立即购买' }}
                </el-button>
                <el-button
                  v-if="!showTemplates"
                  size="small"
                  @click.stop="addToCart(item)"
                >
                  加入购物车
                </el-button>
                <el-button
                  v-if="showTemplates"
                  size="small"
                  type="info"
                  @click.stop="viewTemplateDetail(item)"
                >
                  查看详情
                </el-button>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 空状态 -->
    <div v-if="products.length === 0" class="empty-state">
      <el-empty description="暂无项目源码">
        <el-button type="primary" @click="clearFilters">清除筛选</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import placeholderImage from '@/assets/images/placeholder.svg'
import { productApi } from '@/api/product'
import { useCartStore } from '@/stores/cart'
import type { Product, Category } from '@/types/product'

const router = useRouter()
const cartStore = useCartStore()

// 数据
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const orderTemplates = ref<OrderTemplate[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const selectedCategory = ref<number | null>(null)
const searchQuery = ref('')
const loading = ref(false)
const showTemplates = ref(false)

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

// 计算属性
const skip = computed(() => (currentPage.value - 1) * pageSize.value)

// 当前显示的数据
const currentItems = computed(() => {
  return showTemplates.value ? orderTemplates.value : products.value
})

// 方法
const loadCategories = async () => {
  try {
    const response = await productApi.getCategories()
    categories.value = response.data
  } catch (error) {
    ElMessage.error('加载分类失败')
  }
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      skip: skip.value,
      limit: pageSize.value,
      category_id: selectedCategory.value || undefined,
      search: searchQuery.value || undefined,
    }

    const response = await productApi.getProducts(params)
    products.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const selectCategory = (categoryId: number | null) => {
  selectedCategory.value = categoryId
  currentPage.value = 1
  loadProducts()
}

const handleSearch = () => {
  currentPage.value = 1
  loadProducts()
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

const viewProduct = (productId: number) => {
  router.push(`/products/${productId}`)
}

const buyProduct = (product: Product) => {
  if (!product.is_active) {
    ElMessage.warning('商品已下架')
    return
  }
  if (product.stock <= 0) {
    ElMessage.warning('商品缺货')
    return
  }

  // 跳转到商品详情页购买
  router.push(`/products/${product.id}`)
}

const addToCart = (product: Product) => {
  if (!product.is_active) {
    ElMessage.warning('商品已下架')
    return
  }
  if (product.stock <= 0) {
    ElMessage.warning('商品缺货')
    return
  }

  cartStore.addItem(product.id, 1, product.price, product.name, product.image_url)
  ElMessage.success('已添加到购物车')
}

const loadOrderTemplates = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取订单模板列表
    // 这里使用模拟数据
    orderTemplates.value = [
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
        image_url: placeholderImage,
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
        support_count: 0,
        image_url: placeholderImage,
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
        image_url: placeholderImage,
        is_active: true,
        created_at: '2024-12-03T12:00:00Z',
      },
    ].filter(template => template.is_active)
  } catch (error) {
    ElMessage.error('加载定制开发项目失败')
  } finally {
    loading.value = false
  }
}

const toggleTemplates = () => {
  showTemplates.value = !showTemplates.value
  if (showTemplates.value) {
    loadOrderTemplates()
  } else {
    loadProducts()
  }
  selectedCategory.value = null
  searchQuery.value = ''
  currentPage.value = 1
}

const clearFilters = () => {
  selectedCategory.value = null
  searchQuery.value = ''
  currentPage.value = 1
  if (showTemplates.value) {
    loadOrderTemplates()
  } else {
    loadProducts()
  }
}

// 工具方法
const getCategoryName = (category: string) => {
  const categoryMap = {
    'web': 'Web开发',
    'mobile': '移动开发',
    'tool': '工具软件',
    'api': 'API服务',
    'data': '数据分析',
    'other': '其他',
  }
  return categoryMap[category] || category
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

const viewTemplate = (template: OrderTemplate) => {
  // 直接跳转到详情页面
  viewTemplateDetail(template)
}

const buyTemplate = (template: OrderTemplate) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (!template.is_active) {
    ElMessage.warning('该项目已下架')
    return
  }

  // 跳转到订单创建页面，传递模板信息
  router.push({
    path: '/checkout',
    query: {
      templateId: template.id,
      type: 'template'
    }
  })
}

const viewTemplateDetail = (template: OrderTemplate) => {
  // 显示模板详情对话框
  ElMessage.info(`查看模板详情: ${template.title}`)
  // 这里可以打开一个详情对话框
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = placeholderImage
}

// 生命周期
onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>

<style scoped>
.products {
  padding: 20px 0;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding: 0 20px;
}

.search-bar {
  max-width: 400px;
  margin: 0 auto 30px;
  padding: 0 20px;
}

.products-grid {
  padding: 0 20px;
}

.product-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
  border-radius: 4px;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-status {
  position: absolute;
  top: 10px;
  right: 10px;
}

.product-info {
  padding: 15px 0;
}

.product-name {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-description {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.current-price {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.original-price {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

.product-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

.product-category {
  margin-bottom: 15px;
}

.product-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

@media (max-width: 768px) {
  .categories {
    padding: 0 10px;
  }

  .search-bar {
    padding: 0 10px;
  }

  .products-grid {
    padding: 0 10px;
  }

  .product-actions {
    flex-direction: column;
  }
}
</style>

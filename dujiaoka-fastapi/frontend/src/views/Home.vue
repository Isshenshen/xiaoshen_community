<template>
  <div class="home">
    <!-- Hero 区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-emoji">🌈</div>
        <h1>小申交流站</h1>
        <p class="hero-subtitle">分享学习，共同成长</p>
        <p class="hero-desc">发现优质学习资源，和志同道合的小伙伴一起进步 ✨</p>
        <div class="hero-buttons">
          <el-button type="primary" size="large" round @click="goToProducts">
            🔍 探索资源
          </el-button>
          <el-button size="large" round @click="goToAbout">
            💡 了解更多
          </el-button>
        </div>
      </div>
      <div class="hero-decoration">
        <div class="floating-shape shape-1">💻</div>
        <div class="floating-shape shape-2">📚</div>
        <div class="floating-shape shape-3">🚀</div>
        <div class="floating-shape shape-4">💡</div>
      </div>
    </div>

    <!-- 特色卡片 -->
    <div class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">✨</span>
          <h2>为什么选择我们</h2>
        </div>
        <el-row :gutter="24">
          <el-col :xs="24" :sm="8" v-for="feature in features" :key="feature.id">
            <div class="feature-card">
              <div class="feature-icon">{{ feature.emoji }}</div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 热门资源 -->
    <div class="products-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">🔥</span>
          <h2>热门资源</h2>
          <el-button type="primary" text @click="goToProducts">
            查看全部 →
          </el-button>
        </div>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" v-for="product in hotProducts" :key="product.id">
            <div class="product-card" @click="viewProduct(product.id)">
              <div class="product-image">
                <img :src="product.image_url || placeholderImage" :alt="product.name" />
                <div class="product-tag">热门</div>
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <div class="product-meta">
                  <span class="price">¥{{ product.price }}</span>
                  <span class="sold">{{ product.sold_count }}人学习</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 数据统计 -->
    <div class="stats-section">
      <div class="container">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6" v-for="stat in stats" :key="stat.id">
            <div class="stat-card">
              <div class="stat-emoji">{{ stat.emoji }}</div>
              <div class="stat-number">{{ stat.number }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 底部 CTA -->
    <div class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>准备好开始学习了吗？ 🎯</h2>
          <p>加入我们，和小伙伴们一起成长吧！</p>
          <el-button type="primary" size="large" round @click="$router.push('/register')">
            立即加入 →
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import placeholderImage from '@/assets/images/placeholder.svg'

const router = useRouter()

// 特色功能
const features = ref([
  {
    id: 1,
    emoji: '📦',
    title: '优质资源',
    description: '精选高质量学习资料，助你快速成长',
  },
  {
    id: 2,
    emoji: '🛡️',
    title: '安全可靠',
    description: '所有资源经过审核，放心学习无忧',
  },
  {
    id: 3,
    emoji: '💬',
    title: '交流分享',
    description: '和志同道合的小伙伴一起学习讨论',
  },
])

// 热门资源
const hotProducts = ref([
  {
    id: 1,
    name: 'Vue3全栈博客系统',
    price: 99.00,
    sold_count: 128,
    image_url: placeholderImage,
  },
  {
    id: 2,
    name: 'React Native电商App',
    price: 199.00,
    sold_count: 89,
    image_url: placeholderImage,
  },
  {
    id: 3,
    name: 'Python后端模板',
    price: 79.00,
    sold_count: 156,
    image_url: placeholderImage,
  },
  {
    id: 4,
    name: '小程序商城源码',
    price: 149.00,
    sold_count: 67,
    image_url: placeholderImage,
  },
])

// 统计数据
const stats = ref([
  { id: 1, emoji: '👥', number: '2,000+', label: '小伙伴' },
  { id: 2, emoji: '📚', number: '500+', label: '学习资源' },
  { id: 3, emoji: '⭐', number: '98%', label: '好评率' },
  { id: 4, emoji: '🏆', number: '4.9', label: '用户评分' },
])

const goToProducts = () => {
  router.push('/products')
}

const goToAbout = () => {
  router.push('/about')
}

const viewProduct = (productId: number) => {
  router.push(`/products/${productId}`)
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

/* Hero 区域 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
  border-radius: 0 0 50px 50px;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 600px;
  margin: 0 auto;
}

.hero-emoji {
  font-size: 64px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

.hero-section h1 {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 10px 0;
  letter-spacing: 2px;
}

.hero-subtitle {
  font-size: 24px;
  opacity: 0.95;
  margin: 0 0 15px 0;
  font-weight: 500;
}

.hero-desc {
  font-size: 16px;
  opacity: 0.85;
  margin: 0 0 30px 0;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-buttons :deep(.el-button--primary) {
  background: white;
  color: #667eea;
  border: none;
  padding: 12px 30px;
  font-weight: 600;
}

.hero-buttons :deep(.el-button--default) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
  padding: 12px 30px;
}

/* 浮动装饰 */
.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  font-size: 40px;
  opacity: 0.3;
  animation: float 6s ease-in-out infinite;
}

.shape-1 { top: 15%; left: 10%; animation-delay: 0s; }
.shape-2 { top: 25%; right: 15%; animation-delay: 1s; }
.shape-3 { bottom: 20%; left: 15%; animation-delay: 2s; }
.shape-4 { bottom: 30%; right: 10%; animation-delay: 3s; }

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

/* 通用容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 区块标题 */
.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.section-emoji {
  font-size: 28px;
}

.section-header h2 {
  margin: 0;
  font-size: 28px;
  color: #303133;
  font-weight: 600;
}

/* 特色区域 */
.features-section {
  padding: 80px 20px;
  background: white;
}

.feature-card {
  text-align: center;
  padding: 40px 25px;
  border-radius: 20px;
  background: linear-gradient(145deg, #f8f9ff 0%, #fff 100%);
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.feature-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
  line-height: 1.6;
}

/* 热门资源 */
.products-section {
  padding: 80px 20px;
  background: linear-gradient(180deg, #f8f9ff 0%, #fff 100%);
}

.products-section .section-header {
  justify-content: space-between;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 20px;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
}

.product-image {
  position: relative;
  height: 160px;
  overflow: hidden;
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

.product-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.product-info {
  padding: 16px;
}

.product-info h3 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.sold {
  font-size: 12px;
  color: #909399;
}

/* 统计区域 */
.stats-section {
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card {
  text-align: center;
  padding: 30px 15px;
  color: white;
}

.stat-emoji {
  font-size: 36px;
  margin-bottom: 10px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.85;
}

/* CTA 区域 */
.cta-section {
  padding: 80px 20px;
  background: white;
}

.cta-content {
  text-align: center;
  max-width: 500px;
  margin: 0 auto;
}

.cta-content h2 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 15px 0;
}

.cta-content p {
  font-size: 16px;
  color: #909399;
  margin: 0 0 30px 0;
}

.cta-content :deep(.el-button) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 14px 40px;
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-section {
    padding: 60px 20px;
    border-radius: 0 0 30px 30px;
  }

  .hero-section h1 {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .hero-emoji {
    font-size: 48px;
  }

  .floating-shape {
    font-size: 28px;
    opacity: 0.2;
  }

  .section-header h2 {
    font-size: 22px;
  }

  .features-section,
  .products-section,
  .cta-section {
    padding: 50px 15px;
  }
}
</style>

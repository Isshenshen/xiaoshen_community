<template>
  <div class="about">
    <!-- Hero 区域 -->
    <div class="hero-section">
      <div class="container">
        <div class="hero-content">
          <div class="hero-text">
            <div class="hero-emoji">👋</div>
            <h1>关于小申交流站</h1>
            <p class="subtitle">分享学习 · 交流成长 · 共同进步</p>
            <p class="description">
              这是一个为学习者打造的交流平台，在这里你可以找到优质的学习资源，
              认识志同道合的小伙伴，一起学习，一起成长！💪
            </p>
            <div class="hero-stats">
              <div class="stat">
                <div class="number">{{ stats.resources }}+</div>
                <div class="label">学习资源</div>
              </div>
              <div class="stat">
                <div class="number">{{ stats.users }}+</div>
                <div class="label">小伙伴</div>
              </div>
              <div class="stat">
                <div class="number">{{ stats.satisfaction }}%</div>
                <div class="label">满意度</div>
              </div>
            </div>
          </div>
          <div class="hero-image">
            <div class="avatar-container">
              <div class="avatar-emoji">🌟</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 我们的特色 -->
    <div class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">✨</span>
          <h2>我们的特色</h2>
        </div>
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="6" v-for="feature in features" :key="feature.id">
            <div class="feature-card">
              <div class="feature-emoji">{{ feature.emoji }}</div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 技术栈 -->
    <div class="tech-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">🛠️</span>
          <h2>技术支持</h2>
        </div>
        <div class="tech-grid">
          <div v-for="tech in techStack" :key="tech.name" class="tech-card">
            <div class="tech-emoji">{{ tech.emoji }}</div>
            <div class="tech-info">
              <h3>{{ tech.name }}</h3>
              <p>{{ tech.description }}</p>
              <el-progress
                :percentage="tech.level"
                :show-text="false"
                :stroke-width="6"
                color="#667eea"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 发展历程 -->
    <div class="timeline-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">📅</span>
          <h2>发展历程</h2>
        </div>
        <div class="timeline">
          <div v-for="(item, index) in timeline" :key="index" class="timeline-item">
            <div class="timeline-dot">{{ item.emoji }}</div>
            <div class="timeline-content">
              <div class="timeline-date">{{ item.date }}</div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速开始 -->
    <div class="guide-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">🚀</span>
          <h2>快速开始</h2>
        </div>
        <div class="guide-steps">
          <div v-for="step in guideSteps" :key="step.id" class="guide-step">
            <div class="step-number">{{ step.id }}</div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系我们 -->
    <div class="contact-section">
      <div class="container">
        <div class="section-header">
          <span class="section-emoji">💌</span>
          <h2>联系我们</h2>
        </div>
        <div class="contact-grid">
          <div v-for="contact in contacts" :key="contact.type" class="contact-card">
            <div class="contact-emoji">{{ contact.emoji }}</div>
            <div class="contact-info">
              <h3>{{ contact.title }}</h3>
              <p>{{ contact.value }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>准备好加入我们了吗？ 🎉</h2>
          <p>和小伙伴们一起学习，一起成长！</p>
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

// 统计数据
const stats = ref({
  resources: 500,
  users: 2000,
  satisfaction: 98,
})

// 特色功能
const features = ref([
  {
    id: 1,
    emoji: '📚',
    title: '丰富资源',
    description: '精选优质学习资料，涵盖多个领域',
  },
  {
    id: 2,
    emoji: '🔒',
    title: '安全可靠',
    description: '所有资源经过审核，保障学习体验',
  },
  {
    id: 3,
    emoji: '💬',
    title: '交流社区',
    description: '志同道合的小伙伴，共同学习成长',
  },
  {
    id: 4,
    emoji: '🎯',
    title: '持续更新',
    description: '定期更新资源，紧跟时代步伐',
  },
])

// 技术栈
const techStack = ref([
  {
    emoji: '💚',
    name: 'Vue 3',
    description: '现代化前端框架，流畅的用户体验',
    level: 95,
  },
  {
    emoji: '⚡',
    name: 'FastAPI',
    description: '高性能 Python 后端，稳定可靠',
    level: 92,
  },
  {
    emoji: '🎨',
    name: 'Element Plus',
    description: '美观的 UI 组件库，简洁大方',
    level: 90,
  },
  {
    emoji: '🗄️',
    name: '数据库',
    description: 'SQLite/PostgreSQL，数据安全',
    level: 88,
  },
])

// 发展历程
const timeline = ref([
  {
    emoji: '🌱',
    date: '2024',
    title: '项目启动',
    description: '小申交流站正式开始开发，确定技术方案',
  },
  {
    emoji: '🚀',
    date: '2025 初',
    title: '功能完善',
    description: '完成核心功能开发，包括资源管理、用户系统',
  },
  {
    emoji: '🎉',
    date: '2025',
    title: '正式上线',
    description: '小申交流站正式对外开放，欢迎小伙伴加入',
  },
])

// 快速开始步骤
const guideSteps = ref([
  {
    id: 1,
    title: '注册账号',
    description: '简单几步，快速创建你的专属账号',
  },
  {
    id: 2,
    title: '浏览资源',
    description: '探索丰富的学习资源，找到你需要的',
  },
  {
    id: 3,
    title: '获取资源',
    description: '一键获取资源，开始你的学习之旅',
  },
  {
    id: 4,
    title: '交流成长',
    description: '和小伙伴们交流分享，共同进步',
  },
])

// 联系方式
const contacts = ref([
  {
    type: 'email',
    emoji: '📧',
    title: '邮箱',
    value: 'hello@xiaoshen.com',
  },
  {
    type: 'website',
    emoji: '🌐',
    title: '网站',
    value: 'xiaoshen.com',
  },
  {
    type: 'docs',
    emoji: '📖',
    title: 'API文档',
    value: '/docs',
  },
  {
    type: 'support',
    emoji: '💡',
    title: '帮助中心',
    value: '随时为你解答',
  },
])
</script>

<style scoped>
.about {
  min-height: 100vh;
}

/* Hero 区域 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  border-radius: 0 0 50px 50px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 250px;
  gap: 60px;
  align-items: center;
}

.hero-emoji {
  font-size: 64px;
  margin-bottom: 15px;
}

.hero-text h1 {
  margin: 0 0 10px 0;
  font-size: 42px;
  font-weight: 700;
}

.subtitle {
  margin: 0 0 20px 0;
  font-size: 20px;
  opacity: 0.9;
}

.description {
  margin: 0 0 40px 0;
  font-size: 16px;
  line-height: 1.8;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  gap: 40px;
}

.stat {
  text-align: center;
}

.stat .number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat .label {
  font-size: 14px;
  opacity: 0.8;
}

.hero-image {
  display: flex;
  justify-content: center;
}

.avatar-container {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.avatar-emoji {
  font-size: 80px;
}

/* 通用区块样式 */
.features-section,
.tech-section,
.timeline-section,
.guide-section,
.contact-section {
  padding: 80px 20px;
}

.features-section,
.guide-section {
  background: white;
}

.tech-section,
.timeline-section,
.contact-section {
  background: #f8f9ff;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 50px;
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

/* 特色卡片 */
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

.feature-emoji {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.feature-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
  line-height: 1.6;
}

/* 技术栈 */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.tech-card {
  display: flex;
  align-items: center;
  padding: 25px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.tech-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
}

.tech-emoji {
  font-size: 40px;
  margin-right: 20px;
}

.tech-info {
  flex: 1;
}

.tech-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.tech-info p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #909399;
}

/* 时间线 */
.timeline {
  max-width: 700px;
  margin: 0 auto;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
  padding-left: 70px;
}

.timeline-dot {
  position: absolute;
  left: 0;
  top: 0;
  width: 50px;
  height: 50px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.timeline-content {
  background: white;
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.timeline-date {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 8px;
}

.timeline-content h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.timeline-content p {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
}

/* 快速开始 */
.guide-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 25px;
  max-width: 1000px;
  margin: 0 auto;
}

.guide-step {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 25px;
  background: linear-gradient(145deg, #f8f9ff 0%, #fff 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.08);
}

.step-number {
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
}

.step-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.step-content p {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

/* 联系我们 */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 25px;
}

.contact-card {
  display: flex;
  align-items: center;
  padding: 25px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.contact-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
}

.contact-emoji {
  font-size: 36px;
  margin-right: 20px;
}

.contact-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.contact-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* CTA */
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
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 40px;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-text h1 {
    font-size: 32px;
  }

  .features-section,
  .tech-section,
  .timeline-section,
  .guide-section,
  .contact-section {
    padding: 50px 15px;
  }

  .timeline::before {
    left: 20px;
  }

  .timeline-item {
    padding-left: 60px;
  }

  .timeline-dot {
    width: 42px;
    height: 42px;
    font-size: 20px;
  }
}
</style>

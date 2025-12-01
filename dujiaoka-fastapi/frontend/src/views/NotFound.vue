<template>
  <div class="not-found">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-message">
        <h1>页面未找到</h1>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
      </div>

      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          返回上一页
        </el-button>
      </div>

      <div class="error-suggestions">
        <h3>您可以尝试：</h3>
        <ul>
          <li>检查网址是否正确</li>
          <li>返回首页浏览项目</li>
          <li>联系管理员获取帮助</li>
        </ul>
      </div>
    </div>

    <div class="error-illustration">
      <div class="illustration">
        <div class="circle"></div>
        <div class="circle"></div>
        <div class="circle"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  text-align: center;
  color: white;
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  margin-bottom: 20px;
  opacity: 0.8;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.error-message h1 {
  margin: 0 0 15px 0;
  font-size: 32px;
  font-weight: 600;
}

.error-message p {
  margin: 0 0 30px 0;
  font-size: 18px;
  opacity: 0.9;
}

.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 40px;
}

.error-suggestions {
  background: rgba(255, 255, 255, 0.1);
  padding: 25px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.error-suggestions h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
}

.error-suggestions ul {
  margin: 0;
  padding-left: 20px;
  text-align: left;
}

.error-suggestions li {
  margin-bottom: 8px;
  opacity: 0.9;
}

.error-illustration {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: -1;
}

.illustration {
  position: relative;
  width: 300px;
  height: 300px;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.circle:nth-child(1) {
  width: 200px;
  height: 200px;
  background: white;
  top: 50px;
  left: 50px;
  animation: float 6s ease-in-out infinite;
}

.circle:nth-child(2) {
  width: 150px;
  height: 150px;
  background: #409eff;
  top: 100px;
  left: 100px;
  animation: float 4s ease-in-out infinite reverse;
}

.circle:nth-child(3) {
  width: 100px;
  height: 100px;
  background: #67c23a;
  top: 150px;
  left: 150px;
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@media (max-width: 768px) {
  .not-found {
    flex-direction: column;
    text-align: center;
  }

  .error-code {
    font-size: 80px;
  }

  .error-message h1 {
    font-size: 24px;
  }

  .error-actions {
    flex-direction: column;
  }

  .illustration {
    width: 200px;
    height: 200px;
  }

  .circle {
    width: 60px !important;
    height: 60px !important;
  }
}
</style>

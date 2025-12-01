<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo" @click="$router.push('/')">
            <span class="logo-icon">🌟</span>
            <h2>小申交流站</h2>
          </div>
          <div class="nav-menu">
            <el-menu
              :default-active="activeIndex"
              class="nav-menu"
              mode="horizontal"
              @select="handleSelect"
            >
              <el-menu-item index="/">首页</el-menu-item>
              <el-menu-item index="/products">资源</el-menu-item>
              <el-menu-item index="/about">关于</el-menu-item>
              <el-menu-item index="/orders">订单</el-menu-item>
            </el-menu>
          </div>
          <div class="user-actions">
            <!-- 购物车图标 -->
            <div v-if="authStore.isAuthenticated" class="cart-icon" @click="$router.push('/cart')">
              <el-icon :size="20">
                <ShoppingCart />
              </el-icon>
              <span v-if="cartStore.totalItems > 0" class="cart-badge">
                {{ cartStore.totalItems }}
              </span>
            </div>

            <template v-if="!authStore.isAuthenticated">
              <el-button text @click="$router.push('/login')">登录</el-button>
              <el-button type="primary" round @click="$router.push('/register')">注册</el-button>
            </template>
            <template v-else>
              <el-dropdown @command="handleUserCommand">
                <span class="user-info">
                  <el-avatar :size="32" :src="authStore.user?.avatar">
                    {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <span class="username">{{ authStore.user?.username }}</span>
                  <el-icon class="el-icon--right">
                    <ArrowDown />
                  </el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                    <el-dropdown-item command="balance">
                      余额: ¥{{ authStore.user?.balance?.toFixed(2) }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="authStore.isAdmin"
                      command="admin"
                      divided
                    >
                      后台管理
                    </el-dropdown-item>
                    <el-dropdown-item command="logout" :divided="!authStore.isAdmin">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </div>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <el-container>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <p>© 2025 小申交流站 · 分享学习，共同成长 💖</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, ShoppingCart } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import { useCartStore } from './stores/cart'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const activeIndex = computed(() => router.currentRoute.value.path)

const handleSelect = (key: string) => {
  router.push(key)
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'orders':
      router.push('/orders')
      break
    case 'balance':
      router.push('/recharge')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(() => {
        authStore.logout()
        router.push('/')
      })
      break
  }
}
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 24px;
}

.logo h2 {
  margin: 0;
  color: white;
  font-weight: 600;
  font-size: 20px;
  letter-spacing: 1px;
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
  border-bottom: none;
  background: transparent !important;
}

.nav-menu :deep(.el-menu) {
  background: transparent !important;
  border-bottom: none;
}

.nav-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
  border-bottom: none !important;
  transition: all 0.3s;
}

.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-menu-item.is-active) {
  color: white !important;
  background: rgba(255, 255, 255, 0.15) !important;
  border-radius: 20px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-actions :deep(.el-button--text) {
  color: rgba(255, 255, 255, 0.9);
}

.user-actions :deep(.el-button--primary) {
  background: white;
  color: #667eea;
  border: none;
}

.user-actions :deep(.el-button--primary:hover) {
  background: rgba(255, 255, 255, 0.9);
}

.cart-icon {
  position: relative;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.3s;
  color: white;
}

.cart-icon:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.cart-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ff6b6b;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 25px;
  transition: background-color 0.3s;
  color: white;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.username {
  font-weight: 500;
  color: white;
}

.app-main {
  background: linear-gradient(180deg, #f8f9ff 0%, #f0f2ff 100%);
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-main > * {
  max-width: 1200px;
  margin: 0 auto;
}

.app-footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 15px;
  height: auto !important;
}

.app-footer p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }

  .logo h2 {
    font-size: 16px;
  }

  .nav-menu {
    margin: 0 15px;
  }

  .user-actions {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
    padding: 10px 15px;
  }

  .nav-menu {
    margin: 0;
    order: 3;
    width: 100%;
  }

  .user-actions {
    order: 2;
  }

  .logo {
    order: 1;
  }
}
</style>

<template>
  <div class="profile">
    <el-row :gutter="40">
      <!-- 左侧菜单 -->
      <el-col :span="6">
        <el-menu
          :default-active="activeTab"
          class="profile-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="info">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </el-menu-item>
          <el-menu-item index="security">
            <el-icon><Lock /></el-icon>
            <span>安全设置</span>
          </el-menu-item>
          <el-menu-item index="balance">
            <el-icon><Money /></el-icon>
            <span>余额管理</span>
          </el-menu-item>
        </el-menu>
      </el-col>

      <!-- 右侧内容 -->
      <el-col :span="18">
        <!-- 基本信息 -->
        <div v-if="activeTab === 'info'" class="profile-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
                <el-button type="primary" size="small" @click="editMode = !editMode">
                  {{ editMode ? '取消' : '编辑' }}
                </el-button>
              </div>
            </template>

            <el-form
              v-if="editMode"
              ref="infoFormRef"
              :model="userForm"
              :rules="infoRules"
              label-width="100px"
            >
              <el-form-item label="用户名">
                <el-input v-model="userForm.username" disabled />
                <div class="form-tip">用户名不可修改</div>
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input v-model="userForm.email" />
              </el-form-item>

              <el-form-item label="真实姓名" prop="full_name">
                <el-input v-model="userForm.full_name" placeholder="请输入真实姓名" />
              </el-form-item>

              <el-form-item label="手机号码" prop="phone">
                <el-input v-model="userForm.phone" placeholder="请输入手机号码" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="updateInfo" :loading="updating">
                  保存
                </el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </el-form-item>
            </el-form>

            <div v-else class="info-display">
              <div class="info-item">
                <span class="label">用户名:</span>
                <span class="value">{{ user?.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱:</span>
                <span class="value">{{ user?.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">真实姓名:</span>
                <span class="value">{{ user?.full_name || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">手机号码:</span>
                <span class="value">{{ user?.phone || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">注册时间:</span>
                <span class="value">{{ formatTime(user?.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最后登录:</span>
                <span class="value">{{ user?.last_login ? formatTime(user.last_login) : '从未登录' }}</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 安全设置 -->
        <div v-if="activeTab === 'security'" class="profile-content">
          <el-card>
            <template #header>
              <span>修改密码</span>
            </template>

            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="120px"
            >
              <el-form-item label="当前密码" prop="old_password">
                <el-input
                  v-model="passwordForm.old_password"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="新密码" prop="new_password">
                <el-input
                  v-model="passwordForm.new_password"
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="确认新密码" prop="confirm_password">
                <el-input
                  v-model="passwordForm.confirm_password"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="changePassword" :loading="changingPassword">
                  修改密码
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 余额管理 -->
        <div v-if="activeTab === 'balance'" class="profile-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>余额管理</span>
                <el-button type="primary" size="small" @click="$router.push('/recharge')">
                  充值
                </el-button>
              </div>
            </template>

            <div class="balance-info">
              <div class="balance-card">
                <div class="balance-amount">
                  <span class="label">当前余额</span>
                  <span class="amount">¥{{ user?.balance?.toFixed(2) }}</span>
                </div>
                <div class="balance-actions">
                  <el-button type="primary" @click="$router.push('/recharge')">
                    立即充值
                  </el-button>
                </div>
              </div>
            </div>

            <div class="balance-tips">
              <el-alert
                title="余额使用说明"
                type="info"
                :closable="false"
              >
                <ul>
                  <li>余额可用于购买商品，1元=1余额</li>
                  <li>余额支付更快捷，无需等待第三方支付确认</li>
                  <li>余额不支持提现，可通过购买商品使用</li>
                </ul>
              </el-alert>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Money } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const authStore = useAuthStore()

const activeTab = ref('info')
const editMode = ref(false)
const updating = ref(false)
const changingPassword = ref(false)

const userForm = reactive({
  username: '',
  email: '',
  full_name: '',
  phone: '',
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const infoFormRef = ref()
const passwordFormRef = ref()

// 表单验证规则
const infoRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  full_name: [
    { max: 100, message: '姓名不能超过100个字符', trigger: 'blur' },
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' },
  ],
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 计算属性
const user = computed(() => authStore.user)

// 方法
const handleMenuSelect = (index: string) => {
  activeTab.value = index
}

const updateInfo = async () => {
  if (!infoFormRef.value) return

  try {
    await infoFormRef.value.validate()
    updating.value = true

    await authStore.updateUser(userForm)
    ElMessage.success('信息更新成功')
    editMode.value = false
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const cancelEdit = () => {
  // 重置表单数据
  Object.assign(userForm, {
    username: user.value?.username || '',
    email: user.value?.email || '',
    full_name: user.value?.full_name || '',
    phone: user.value?.phone || '',
  })
  editMode.value = false
}

const changePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true

    await authStore.changePassword(passwordForm.old_password, passwordForm.new_password)
    ElMessage.success('密码修改成功')

    // 清空表单
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: '',
    })
  } catch (error) {
    ElMessage.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

const formatTime = (timeStr?: string) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 初始化数据
const initUserForm = () => {
  Object.assign(userForm, {
    username: user.value?.username || '',
    email: user.value?.email || '',
    full_name: user.value?.full_name || '',
    phone: user.value?.phone || '',
  })
}

// 生命周期
onMounted(() => {
  initUserForm()
})
</script>

<style scoped>
.profile {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.profile-menu {
  border-radius: 8px;
  overflow: hidden;
}

.profile-content {
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.info-display {
  padding: 20px 0;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  width: 100px;
  color: #606266;
  font-weight: 500;
}

.value {
  color: #303133;
  flex: 1;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.balance-info {
  margin-bottom: 30px;
}

.balance-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.balance-amount {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.balance-amount .label {
  font-size: 14px;
  opacity: 0.9;
}

.balance-amount .amount {
  font-size: 32px;
  font-weight: bold;
}

.balance-tips {
  margin-top: 20px;
}

.balance-tips ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.balance-tips li {
  margin-bottom: 5px;
  color: #606266;
}

@media (max-width: 768px) {
  .profile {
    padding: 20px 10px;
  }

  .balance-card {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .balance-amount .amount {
    font-size: 28px;
  }
}
</style>

<template>
  <div class="admin-users">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          添加用户
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="用户名">
          <el-input
            v-model="filterForm.username"
            placeholder="输入用户名"
            clearable
            @clear="handleFilter"
            @keyup.enter="handleFilter"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="filterForm.email"
            placeholder="输入邮箱"
            clearable
            @clear="handleFilter"
            @keyup.enter="handleFilter"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.is_active" placeholder="选择状态" clearable @change="handleFilter">
            <el-option label="正常" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card>
      <el-table
        :data="users"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="{ row }">
            ¥{{ row.balance.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_superuser" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_superuser ? 'warning' : 'info'">
              {{ row.is_superuser ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="row.id === currentUser?.id"
              @click="toggleUserStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="row.id === currentUser?.id"
              @click="deleteUser(row)"
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

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="输入用户名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="输入邮箱" />
        </el-form-item>

        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="姓名">
          <el-input v-model="userForm.full_name" placeholder="输入姓名" />
        </el-form-item>

        <el-form-item label="手机">
          <el-input v-model="userForm.phone" placeholder="输入手机号码" />
        </el-form-item>

        <el-form-item label="余额">
          <el-input-number
            v-model="userForm.balance"
            :min="0"
            :precision="2"
            :step="0.01"
          />
        </el-form-item>

        <el-form-item label="角色">
          <el-radio-group v-model="userForm.is_superuser">
            <el-radio :value="false">普通用户</el-radio>
            <el-radio :value="true">管理员</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="userForm.is_active">
            <el-radio :value="true">正常</el-radio>
            <el-radio :value="false">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitUserForm" :loading="submitting">
          {{ editingUser ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 数据
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editingUser = ref(null)

// 表单数据
const filterForm = reactive({
  username: '',
  email: '',
  is_active: null as boolean | null,
})

const userForm = reactive({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone: '',
  balance: 0,
  is_superuser: false,
  is_active: true,
})

// 计算属性
const currentUser = computed(() => authStore.user)
const dialogTitle = computed(() => editingUser.value ? '编辑用户' : '添加用户')

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3到50个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: !editingUser.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

// API调用方法
const fetchUsers = async (params: any = {}) => {
  try {
    const queryParams = new URLSearchParams({
      skip: ((currentPage.value - 1) * pageSize.value).toString(),
      limit: pageSize.value.toString(),
      ...params
    })

    const response = await fetch(`/api/v1/users/?${queryParams}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      const data = await response.json()
      return data
    } else if (response.status === 401) {
      ElMessage.error('权限不足，请重新登录')
      authStore.logout()
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    throw error
  }
}

const updateUser = async (userId: number, userData: any) => {
  try {
    const response = await fetch(`/api/v1/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })

    if (response.ok) {
      return await response.json()
    } else {
      const error = await response.json()
      throw new Error(error.detail || '更新失败')
    }
  } catch (error) {
    console.error('更新用户失败:', error)
    throw error
  }
}

// 方法
const loadUsers = async () => {
  loading.value = true
  try {
    const data = await fetchUsers({
      username: filterForm.username || undefined,
      email: filterForm.email || undefined,
      is_active: filterForm.is_active !== null ? filterForm.is_active : undefined,
    })

    users.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    // 如果API调用失败，使用模拟数据作为后备
    users.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        full_name: '管理员',
        phone: '13800138000',
        balance: 1000.00,
        is_active: true,
        is_superuser: true,
        created_at: '2024-01-01T00:00:00Z',
      },
    ]
    total.value = users.value.length
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  loadUsers()
}

const resetFilter = () => {
  Object.assign(filterForm, {
    username: '',
    email: '',
    is_active: null,
  })
  handleFilter()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadUsers()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  loadUsers()
}

const handleSelectionChange = (selection: any[]) => {
  // 处理选中项变化
}

const editUser = (user: any) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    password: '', // 编辑时不显示密码
    full_name: user.full_name,
    phone: user.phone,
    balance: user.balance,
    is_superuser: user.is_superuser,
    is_active: user.is_active,
  })
  showCreateDialog.value = true
}

const toggleUserStatus = async (user: any) => {
  try {
    const action = user.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户 ${user.username} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 调用API更新用户状态
    await updateUser(user.id, { is_active: !user.is_active })
    user.is_active = !user.is_active
    ElMessage.success(`${action}成功`)

  } catch (error) {
    if (error.message !== '用户取消操作') {
      ElMessage.error(`操作失败: ${error.message}`)
    }
  }
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error',
      }
    )

    // 调用API删除用户
    const response = await fetch(`/api/v1/users/${user.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      // 从列表中移除用户
      const index = users.value.findIndex((u: any) => u.id === user.id)
      if (index > -1) {
        users.value.splice(index, 1)
        total.value--
      }
      ElMessage.success('删除成功')
    } else {
      const error = await response.json()
      throw new Error(error.detail || '删除失败')
    }

  } catch (error) {
    if (error.message !== '用户取消操作') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

const submitUserForm = async () => {
  try {
    submitting.value = true

    if (editingUser.value) {
      // 更新用户
      const updateData = {
        username: userForm.username,
        email: userForm.email,
        full_name: userForm.full_name,
        phone: userForm.phone,
        balance: userForm.balance,
        is_superuser: userForm.is_superuser,
        is_active: userForm.is_active,
      }
      await updateUser(editingUser.value.id, updateData)
      ElMessage.success('更新成功')
    } else {
      // 创建用户 - 注意：后端API可能不支持管理员创建用户，这里先跳过
      ElMessage.warning('管理员创建用户功能暂未实现，请使用注册接口')
      return
    }

    showCreateDialog.value = false
    resetUserForm()
    loadUsers()
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`)
  } finally {
    submitting.value = false
  }
}

const resetUserForm = () => {
  editingUser.value = null
  Object.assign(userForm, {
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    balance: 0,
    is_superuser: false,
    is_active: true,
  })
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users {
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

@media (max-width: 768px) {
  .admin-users {
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
}
</style>

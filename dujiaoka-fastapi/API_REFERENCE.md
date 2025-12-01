# 🚀 独角发卡 FastAPI - API 接口参考文档

## 📊 接口概览

**基础信息:**
- **Base URL:** `http://localhost:8000/api/v1`
- **认证方式:** JWT Bearer Token
- **数据格式:** JSON
- **字符编码:** UTF-8

**认证流程:**
```bash
# 1. 用户登录获取token
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass123

# 2. 使用token访问受保护接口
Authorization: Bearer {access_token}
```

---

## 🔐 认证相关 API

### POST /auth/login
**用户登录**
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass123
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /auth/register
**用户注册**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "pass123",
  "full_name": "测试用户"
}
```

### GET /auth/me
**获取当前用户信息**
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

### PUT /auth/me
**更新当前用户信息**
```http
PUT /api/v1/auth/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "新名字",
  "phone": "13800138000"
}
```

### POST /auth/change-password
**修改密码**
```http
POST /api/v1/auth/change-password?old_password=oldpass&new_password=newpass
Authorization: Bearer {token}
```

---

## 👥 用户管理 API

### GET /users/me
**获取当前用户信息**
```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

### PUT /users/me
**更新当前用户信息**
```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "新名字",
  "phone": "13800138000"
}
```

### GET /users/balance
**获取用户余额**
```http
GET /api/v1/users/balance
Authorization: Bearer {token}
```

**响应:**
```json
{
  "balance": 100.50
}
```

### POST /users/recharge
**充值余额**
```http
POST /api/v1/users/recharge?amount=100.00
Authorization: Bearer {token}
```

### POST /users/change-password
**修改密码**
```http
POST /api/v1/users/change-password?old_password=oldpass&new_password=newpass
Authorization: Bearer {token}
```

### GET /users/ (管理员)
**获取用户列表**
```http
GET /api/v1/users/?skip=0&limit=20
Authorization: Bearer {admin_token}
```

### GET /users/{user_id} (管理员)
**获取指定用户信息**
```http
GET /api/v1/users/1
Authorization: Bearer {admin_token}
```

### PUT /users/{user_id} (管理员)
**更新用户信息**
```http
PUT /api/v1/users/1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "full_name": "新名字",
  "is_active": true
}
```

### DELETE /users/{user_id} (管理员)
**删除用户**
```http
DELETE /api/v1/users/1
Authorization: Bearer {admin_token}
```

---

## 📦 商品管理 API

### GET /products/categories
**获取商品分类列表**
```http
GET /api/v1/products/categories
```

### POST /products/categories (管理员)
**创建商品分类**
```http
POST /api/v1/products/categories
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Web开发",
  "description": "Web前端后端开发相关",
  "sort_order": 1
}
```

### PUT /products/categories/{category_id} (管理员)
**更新商品分类**
```http
PUT /api/v1/products/categories/1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "更新后的分类名",
  "description": "更新后的描述"
}
```

### DELETE /products/categories/{category_id} (管理员)
**删除商品分类**
```http
DELETE /api/v1/products/categories/1
Authorization: Bearer {admin_token}
```

### GET /products/
**获取商品列表**
```http
GET /api/v1/products/?skip=0&limit=20&category_id=1&search=vue
```

**查询参数:**
- `skip`: 分页起始位置 (默认: 0)
- `limit`: 返回数量 (默认: 20)
- `category_id`: 分类筛选
- `search`: 搜索关键词

### GET /products/{product_id}
**获取商品详情**
```http
GET /api/v1/products/1
```

### POST /products/ (管理员)
**创建商品**
```http
POST /api/v1/products/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Vue3 + FastAPI 全栈项目",
  "description": "完整的现代化全栈开发项目",
  "price": 99.99,
  "category_id": 1,
  "stock": 100,
  "auto_delivery": true,
  "is_active": true
}
```

### PUT /products/{product_id} (管理员)
**更新商品**
```http
PUT /api/v1/products/1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "更新后的商品名",
  "price": 129.99,
  "stock": 150
}
```

### DELETE /products/{product_id} (管理员)
**删除商品**
```http
DELETE /api/v1/products/1
Authorization: Bearer {admin_token}
```

### POST /products/{product_id}/stock (管理员)
**更新商品库存**
```http
POST /api/v1/products/1/stock?quantity=200
Authorization: Bearer {admin_token}
```

---

## 📋 订单管理 API

### GET /orders/
**获取订单列表**
```http
GET /api/v1/orders/?skip=0&limit=20&status=paid
Authorization: Bearer {token}
```

**查询参数:**
- `skip`: 分页起始位置
- `limit`: 返回数量
- `status`: 订单状态筛选 (pending/paid/delivered/cancelled/refunded)

### GET /orders/{order_id}
**获取订单详情**
```http
GET /api/v1/orders/1
Authorization: Bearer {token}
```

### POST /orders/
**创建单个商品订单**
```http
POST /api/v1/orders/
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 1,
  "payment_method": "balance",
  "user_note": "尽快发货"
}
```

### PUT /orders/{order_id}
**更新订单 (管理员)**
```http
PUT /api/v1/orders/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "delivered",
  "admin_note": "订单已发货"
}
```

### POST /orders/{order_id}/pay
**支付订单**
```http
POST /api/v1/orders/1/pay
Authorization: Bearer {token}
```

### POST /orders/{order_id}/deliver (管理员)
**发货订单**
```http
POST /api/v1/orders/1/deliver
Authorization: Bearer {admin_token}
```

### POST /orders/{order_id}/cancel
**取消订单**
```http
POST /api/v1/orders/1/cancel
Authorization: Bearer {token}
```

### POST /orders/{order_id}/refund (管理员)
**退款订单**
```http
POST /api/v1/orders/1/refund
Authorization: Bearer {admin_token}
```

---

## 💳 支付管理 API

### GET /payments/
**获取支付记录**
```http
GET /api/v1/payments/?skip=0&limit=20
Authorization: Bearer {token}
```

### GET /payments/{payment_id}
**获取支付记录详情**
```http
GET /api/v1/payments/1
Authorization: Bearer {token}
```

### POST /payments/ (管理员)
**创建支付记录**
```http
POST /api/v1/payments/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_id": 1,
  "order_id": 1,
  "amount": 99.99,
  "payment_method": "balance"
}
```

### PUT /payments/{payment_id} (管理员)
**更新支付记录**
```http
PUT /api/v1/payments/1
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "success"
}
```

### DELETE /payments/{payment_id} (管理员)
**删除支付记录**
```http
DELETE /api/v1/payments/1
Authorization: Bearer {admin_token}
```

---

## 👑 后台管理 API

### GET /admin/dashboard/stats
**获取仪表盘统计数据**
```http
GET /api/v1/admin/dashboard/stats
Authorization: Bearer {admin_token}
```

**响应:**
```json
{
  "total_users": 1234,
  "total_orders": 5678,
  "total_revenue": 123456.78,
  "new_users_today": 12,
  "orders_today": 89,
  "revenue_today": 1234.56
}
```

### GET /admin/dashboard/charts
**获取仪表盘图表数据**
```http
GET /api/v1/admin/dashboard/charts?days=30
Authorization: Bearer {admin_token}
```

**响应:**
```json
{
  "order_chart": [
    {"date": "2024-01-01", "orders": 120}
  ],
  "revenue_chart": [
    {"date": "2024-01-01", "revenue": 1200.00}
  ],
  "sales_chart": [
    {"product": "Vue项目", "quantity": 100, "revenue": 10000.00}
  ]
}
```

### GET /admin/system/info
**获取系统信息**
```http
GET /api/v1/admin/system/info
Authorization: Bearer {admin_token}
```

**响应:**
```json
{
  "database_tables": {
    "users": 1234,
    "products": 567,
    "orders": 3456,
    "payments": 2890
  },
  "server_time": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

---

## 📋 错误响应格式

所有API在出错时都会返回统一的错误格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见HTTP状态码:**
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `403`: 权限不足
- `404`: 资源不存在
- `422`: 数据验证失败
- `500`: 服务器内部错误

---

## 🔧 开发工具

### API测试脚本
项目包含完整的API测试脚本：
```bash
# 运行完整API测试
python api_test.py

# 查看测试报告
cat api_test_report.md
```

### API文档
- **Swagger UI:** `http://localhost:8000/api/v1/openapi.json`
- **交互式文档:** `http://localhost:8000/docs`

---

**最后更新:** 2025年11月30日
**API版本:** v1.0
**状态:** ✅ 生产就绪

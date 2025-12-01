"""
API包初始化文件

本包包含了整个后端API的所有路由模块：

主要API模块：
├── auth.py          # 用户认证相关API（注册、登录、用户信息管理）
├── users.py         # 用户管理API（用户信息查询和更新）
├── products.py      # 商品管理API（商品CRUD、分类管理、库存管理）
├── orders.py        # 订单管理API（订单创建、状态管理、购物车结算）
├── cards.py         # 卡密管理API（卡密CRUD、批量导入、状态管理）
├── payments.py      # 支付管理API（支付记录、支付回调、退款处理）
├── admin.py         # 后台管理API（统计数据、图表数据、系统信息）
└── api_v1/          # API版本控制目录
    └── api.py       # 主路由聚合文件

API设计原则：
- RESTful风格的URL设计
- 统一的响应格式
- 完善的错误处理
- 详细的中文文档
- JWT身份认证
- 基于角色的权限控制

安全特性：
- 密码bcrypt加密
- JWT令牌认证
- 请求频率限制（可扩展）
- CORS跨域支持
- 输入数据验证
- SQL注入防护

使用说明：
所有API都通过/api/v1/前缀访问，例如：
- POST /api/v1/auth/login     # 用户登录
- GET  /api/v1/products/      # 获取商品列表
- POST /api/v1/orders/        # 创建订单

API文档访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json
"""

"""
API v1 路由聚合
"""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.admin import router as admin_router
# from app.api.cards import router as cards_router  # 卡密功能已禁用

api_router = APIRouter()

# 包含所有子路由 - 使用正确的prefix配置
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
# api_router.include_router(cards_router, prefix="/cards", tags=["cards"])  # 卡密功能已禁用

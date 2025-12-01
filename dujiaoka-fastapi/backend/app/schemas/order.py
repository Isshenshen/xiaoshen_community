"""
订单相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from .product import Product
from .user import User


class OrderBase(BaseModel):
    """订单基础模型"""
    product_id: int
    quantity: int = Field(1, gt=0)
    payment_method: str = Field(..., pattern="^(balance|alipay|wechat)$")
    user_note: Optional[str] = None


class OrderCreate(OrderBase):
    """订单创建模型"""
    pass


class OrderUpdate(BaseModel):
    """订单更新模型"""
    status: Optional[str] = None
    admin_note: Optional[str] = None


class Order(OrderBase):
    """订单模型"""
    id: int
    order_number: str
    user_id: int
    product_name: str
    product_price: float
    total_amount: float
    status: str
    delivery_content: Optional[str]
    delivered_at: Optional[datetime]
    admin_note: Optional[str]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]

    # 关联对象
    user: Optional[User]
    product: Optional[Product]

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """订单列表响应"""
    items: List[Order]
    total: int
    page: int
    size: int


class CartItem(BaseModel):
    """购物车项"""
    product_id: int
    quantity: int = Field(1, gt=0)


class OrderSummary(BaseModel):
    """订单摘要"""
    items: List[CartItem]
    total_amount: float

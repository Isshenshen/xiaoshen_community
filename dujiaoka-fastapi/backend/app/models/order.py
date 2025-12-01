"""
订单模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    DELIVERED = "delivered" # 已发货
    CANCELLED = "cancelled" # 已取消
    REFUNDED = "refunded"   # 已退款


class PaymentMethod(str, enum.Enum):
    """支付方式枚举"""
    BALANCE = "balance"     # 余额支付
    ALIPAY = "alipay"       # 支付宝
    WECHAT = "wechat"       # 微信支付


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)  # 订单号

    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 商品信息
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)  # 快照商品名称
    product_price = Column(Float, nullable=False)      # 快照商品价格

    # 订单信息
    quantity = Column(Integer, default=1, nullable=False)
    total_amount = Column(Float, nullable=False)       # 总金额
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    # 发货信息
    delivery_content = Column(Text)  # 发货内容（卡密等）
    delivered_at = Column(DateTime)  # 发货时间

    # 备注
    user_note = Column(Text)         # 用户备注
    admin_note = Column(Text)        # 管理员备注

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    paid_at = Column(DateTime)       # 支付时间

    # 关联关系
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"

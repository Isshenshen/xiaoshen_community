"""
支付记录模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"     # 待支付
    SUCCESS = "success"     # 支付成功
    FAILED = "failed"       # 支付失败
    CANCELLED = "cancelled" # 已取消
    REFUNDED = "refunded"   # 已退款


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # 支付信息
    payment_method = Column(String(20), nullable=False)  # alipay, wechat, balance
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # 第三方支付信息
    transaction_id = Column(String(100), unique=True)  # 第三方交易号
    payment_data = Column(Text)  # 支付相关数据（JSON格式）

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    paid_at = Column(DateTime)  # 支付完成时间

    # 关联关系
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status})>"

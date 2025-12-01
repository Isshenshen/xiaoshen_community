"""
卡密模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CardStatus(str, enum.Enum):
    """卡密状态枚举"""
    UNUSED = "unused"     # 未使用
    USED = "used"         # 已使用
    LOCKED = "locked"     # 已锁定
    EXPIRED = "expired"   # 已过期


class Card(Base):
    """卡密表"""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    # 关联商品
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # 卡密内容（加密存储）
    encrypted_content = Column(Text, nullable=False)  # 加密后的卡密内容
    card_secret = Column(String(128), nullable=False)  # 解密密钥

    # 状态信息
    status = Column(Enum(CardStatus), default=CardStatus.UNUSED, nullable=False)
    used_by = Column(Integer, ForeignKey("users.id"))  # 使用者ID
    used_at = Column(DateTime)  # 使用时间

    # 订单关联（如果是通过订单发放的）
    order_id = Column(Integer, ForeignKey("orders.id"))

    # 有效期
    expires_at = Column(DateTime)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    product = relationship("Product", back_populates="cards")
    user = relationship("User", foreign_keys=[used_by])
    order = relationship("Order", foreign_keys=[order_id])

    def __repr__(self):
        return f"<Card(id={self.id}, product_id={self.product_id}, status={self.status})>"

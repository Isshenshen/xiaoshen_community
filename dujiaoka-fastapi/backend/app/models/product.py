"""
商品模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    """商品分类表"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # 原价

    # 分类
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)

    # 项目信息
    stock = Column(Integer, default=-1, nullable=False)  # 库存(-1表示无限)
    sold_count = Column(Integer, default=0, nullable=False)  # 已售数量
    auto_delivery = Column(Boolean, default=True, nullable=False)  # 是否自动发货

    # 源码项目特有字段
    project_url = Column(String(500))  # 项目演示地址
    download_url = Column(String(500))  # 下载地址
    tech_stack = Column(String(200))  # 技术栈
    project_type = Column(String(50))  # 项目类型: web/app/tool等
    difficulty_level = Column(String(20))  # 难度级别: 入门/中级/高级

    # 状态
    is_active = Column(Boolean, default=True, nullable=False)  # 是否上架
    sort_order = Column(Integer, default=0)

    # 图片
    image_url = Column(String(500))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    category = relationship("Category", back_populates="products")
    orders = relationship("Order", back_populates="product")
    cards = relationship("Card", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"

"""
商品相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """分类创建模型"""
    pass


class CategoryUpdate(BaseModel):
    """分类更新模型"""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class Category(CategoryBase):
    """分类模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """商品基础模型"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    stock: int = Field(-1, ge=-1)  # -1表示无限库存
    auto_delivery: bool = True
    is_active: bool = True
    sort_order: int = 0
    image_url: Optional[str] = None

    # 源码项目字段
    project_url: Optional[str] = None
    download_url: Optional[str] = None
    tech_stack: Optional[str] = None
    project_type: Optional[str] = None
    difficulty_level: Optional[str] = None


class ProductCreate(ProductBase):
    """商品创建模型"""
    pass


class ProductUpdate(BaseModel):
    """商品更新模型"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    stock: Optional[int] = Field(None, ge=0)
    auto_delivery: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    image_url: Optional[str] = None


class Product(ProductBase):
    """商品模型"""
    id: int
    sold_count: int
    category: Optional[Category]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    """商品列表响应"""
    items: List[Product]
    total: int
    page: int
    size: int

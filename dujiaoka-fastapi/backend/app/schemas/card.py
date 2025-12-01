"""
卡密相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CardBase(BaseModel):
    """卡密基础模型"""
    product_id: int
    encrypted_content: str
    expires_at: Optional[datetime] = None


class CardCreate(CardBase):
    """卡密创建模型"""
    pass


class CardUpdate(BaseModel):
    """卡密更新模型"""
    status: Optional[str] = None
    expires_at: Optional[datetime] = None


class Card(BaseModel):
    """卡密模型"""
    id: int
    product_id: int
    status: str
    used_by: Optional[int]
    used_at: Optional[datetime]
    order_id: Optional[int]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardImport(BaseModel):
    """卡密导入模型"""
    product_id: int
    cards: List[str] = Field(..., min_items=1)  # 卡密内容列表


class CardBatchCreate(BaseModel):
    """批量创建卡密"""
    product_id: int
    card_contents: List[str]
    expires_at: Optional[datetime] = None


class CardList(BaseModel):
    """卡密列表响应"""
    items: List[Card]
    total: int
    page: int
    size: int

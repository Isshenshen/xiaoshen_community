"""
支付相关的Pydantic模型
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PaymentBase(BaseModel):
    """支付基础模型"""
    user_id: int
    order_id: int
    payment_method: str
    amount: float


class PaymentCreate(PaymentBase):
    """支付创建模型"""
    pass


class PaymentUpdate(BaseModel):
    """支付更新模型"""
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_data: Optional[str] = None


class Payment(PaymentBase):
    """支付模型"""
    id: int
    status: str
    transaction_id: Optional[str]
    payment_data: Optional[str]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentList(BaseModel):
    """支付列表响应"""
    items: List[Payment]
    total: int
    page: int
    size: int


class AlipayCallback(BaseModel):
    """支付宝回调数据"""
    out_trade_no: str
    trade_no: str
    total_amount: str
    trade_status: str
    sign: str


class WechatCallback(BaseModel):
    """微信支付回调数据"""
    return_code: str
    result_code: str
    out_trade_no: str
    transaction_id: str
    total_fee: str
    sign: str

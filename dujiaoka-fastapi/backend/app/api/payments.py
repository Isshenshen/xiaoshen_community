"""
支付管理API

提供支付记录的查询和管理功能，包括：
- 支付记录查询和筛选
- 支付状态管理
- 第三方支付回调处理
- 支付统计和报表
- 退款处理

支持的支付方式：
- 余额支付：直接从用户余额扣款
- 支付宝：集成支付宝当面付
- 微信支付：集成微信支付

权限说明：
- 普通用户：只能查看自己的支付记录
- 管理员：可以查看和管理所有支付记录

安全考虑：
- 支付金额验证和防重复支付
- 支付回调签名验证
- 敏感支付信息加密存储
- 支付状态变更日志记录

业务规则：
- 支付成功后自动更新订单状态
- 支持部分退款和全额退款
- 支付失败后订单状态不变
- 支付超时自动取消订单
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_superuser
from app.models.user import User
from app.schemas.payment import (
    Payment as PaymentSchema,
    PaymentCreate,
    PaymentUpdate,
    PaymentList
)
from app.services.payment import payment_service

# 创建支付管理路由器
router = APIRouter(
    tags=["支付管理"]   # API文档分组标签
)


@router.get(
    "/",
    response_model=PaymentList,
    summary="获取支付记录",
    description="""
    获取用户的支付记录列表，支持分页查询。

    **查询参数：**
    - `skip`: 跳过的记录数（分页起始位置）
    - `limit`: 返回记录数（1-100）

    **权限控制：**
    - 普通用户：只能查看自己的支付记录
    - 管理员：可以查看所有支付记录

    **返回信息：**
    - 支付ID、订单号、金额
    - 支付方式、支付状态
    - 支付时间、完成时间
    - 第三方支付流水号等

    **排序：** 按支付时间倒序
    """,
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未认证"}
    }
)
async def read_payments(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取支付记录列表

    根据用户权限返回相应的支付记录，支持分页查询。
    普通用户只能查看自己的支付记录，管理员可以查看所有记录。

    Args:
        skip: 分页起始位置
        limit: 返回记录数
        current_user: 当前用户
        db: 数据库会话

    Returns:
        PaymentList: 分页的支付记录列表
    """
    # 普通用户只能查看自己的支付记录，管理员可以查看所有
    user_id = None if current_user.is_superuser else current_user.id

    payments = await payment_service.get_payments(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

    # 获取总数（简化版）
    total = len(payments) if len(payments) < limit else skip + limit + 1

    return PaymentList(
        items=payments,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{payment_id}", response_model=PaymentSchema)
async def read_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取支付记录详情"""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )

    # 检查权限
    if not current_user.is_superuser and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此支付记录"
        )

    return payment


@router.post("/alipay/callback")
async def alipay_callback(
    callback_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """支付宝支付回调"""
    try:
        result = await payment_service.handle_alipay_callback(db, callback_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/wechat/callback")
async def wechat_callback(
    callback_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """微信支付回调"""
    try:
        result = await payment_service.handle_wechat_callback(db, callback_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# 管理员专用API
@router.post("/", response_model=PaymentSchema)
async def create_payment(
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """创建支付记录（管理员）"""
    try:
        payment = await payment_service.create_payment(db, payment_in)
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{payment_id}", response_model=PaymentSchema)
async def update_payment(
    payment_id: int,
    payment_in: PaymentUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """更新支付记录（管理员）"""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )

    try:
        updated_payment = await payment_service.update_payment(db, payment, payment_in)
        return updated_payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """删除支付记录（管理员）"""
    payment = await payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支付记录不存在"
        )

    await payment_service.delete_payment(db, payment)
    return {"message": "支付记录已删除"}

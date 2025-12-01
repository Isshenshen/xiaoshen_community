"""
订单管理API

提供完整的订单生命周期管理功能，包括：
- 订单创建和查询
- 订单状态更新
- 购物车结算
- 订单支付处理
- 自动发货管理

权限说明：
- 普通用户：只能查看和管理自己的订单
- 管理员：可以查看和管理所有订单

订单状态流转：
pending -> paid -> delivered -> completed
    ↓       ↓        ↓
 cancelled  refunded

业务规则：
- 订单创建后24小时内未支付自动取消
- 支付成功后自动触发发货逻辑
- 支持余额支付和第三方支付
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_superuser
from app.models.user import User
from app.models.order import OrderStatus
from app.schemas.order import (
    Order as OrderSchema,
    OrderCreate,
    OrderUpdate,
    OrderList,
    CartItem,
    OrderSummary
)
from app.services.order import order_service

# 创建订单管理路由器
router = APIRouter(
    tags=["订单管理"]  # API文档分组标签
)


@router.get(
    "/",
    response_model=OrderList,
    summary="获取订单列表",
    description="""
    获取用户的订单列表，支持状态筛选和分页。

    **查询参数：**
    - `status`: 订单状态筛选（可选）
      - `pending`: 待支付
      - `paid`: 已支付
      - `delivered`: 已发货
      - `cancelled`: 已取消
      - `refunded`: 已退款
    - `skip`: 跳过的记录数（分页）
    - `limit`: 返回记录数（1-100）

    **权限控制：**
    - 普通用户：只能查看自己的订单
    - 管理员：可以查看所有订单

    **排序：** 按创建时间倒序
    """,
    responses={
        200: {"description": "获取成功"},
        400: {"description": "无效的状态参数"},
        401: {"description": "未认证"}
    }
)
async def read_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单列表

    根据用户权限返回相应的订单列表，支持状态筛选和分页。
    普通用户只能查看自己的订单，管理员可以查看所有订单。

    Args:
        status: 订单状态筛选（可选）
        skip: 分页起始位置
        limit: 返回记录数
        current_user: 当前用户
        db: 数据库会话

    Returns:
        OrderList: 分页的订单列表

    Raises:
        HTTPException: 当状态参数无效时抛出400错误
    """
    order_status = None
    if status:
        try:
            order_status = OrderStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的订单状态"
            )

    # 权限控制：普通用户只能查看自己的订单，管理员可以查看所有
    user_id = None if current_user.is_superuser else current_user.id

    orders = await order_service.get_orders(
        db,
        user_id=user_id,
        status=order_status,
        skip=skip,
        limit=limit
    )

    # 获取总数（简化版）
    total = len(orders) if len(orders) < limit else skip + limit + 1

    return OrderList(
        items=orders,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get(
    "/{order_id}",
    response_model=OrderSchema,
    summary="获取订单详情",
    description="""
    根据订单ID获取单个订单的详细信息。

    **路径参数：**
    - `order_id`: 订单ID（必填）

    **权限控制：**
    - 普通用户：只能查看自己的订单
    - 管理员：可以查看所有订单

    **返回信息：**
    - 订单基本信息（ID、编号、状态、金额等）
    - 商品信息（名称、价格、数量）
    - 用户信息（用户名、邮箱）
    - 时间信息（创建、支付、发货时间）
    - 备注信息（用户备注、管理员备注）
    """,
    responses={
        200: {"description": "获取成功"},
        403: {"description": "无权查看此订单"},
        404: {"description": "订单不存在"}
    }
)
async def read_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单详情

    根据订单ID查询订单详细信息，包含关联的商品和用户信息。
    严格的权限控制确保用户只能查看自己的订单。

    Args:
        order_id: 订单ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        OrderSchema: 订单详细信息

    Raises:
        HTTPException: 当订单不存在或无权限查看时抛出相应错误
    """
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 权限检查：普通用户只能查看自己的订单
    if not current_user.is_superuser and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )

    return order


@router.post(
    "/",
    response_model=OrderSchema,
    summary="创建单个商品订单",
    description="""
    为指定商品创建新的订单。

    **输入参数：**
    - `product_id`: 商品ID（必填）
    - `quantity`: 购买数量（必填）
    - `payment_method`: 支付方式（必填）
      - `balance`: 余额支付
      - `alipay`: 支付宝
      - `wechat`: 微信支付
    - `user_note`: 用户备注（可选）

    **业务逻辑：**
    1. 验证商品存在且上架
    2. 检查库存是否充足
    3. 计算订单总价
    4. 创建订单记录
    5. 扣减商品库存

    **注意：** 创建后订单状态为`pending`，需要支付后才生效
    """,
    responses={
        200: {"description": "订单创建成功"},
        400: {"description": "商品不存在、库存不足或数据无效"},
        401: {"description": "未认证"}
    }
)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建订单"""
    try:
        order = await order_service.create_order(db, order_in, current_user)
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/cart",
    response_model=OrderSummary,
    summary="购物车批量结算",
    description="""
    从购物车批量创建订单，支持多个商品同时购买。

    **输入参数：**
    - `items`: 购物车商品列表
      - `product_id`: 商品ID
      - `quantity`: 购买数量
    - `payment_method`: 支付方式（默认余额支付）
    - `user_note`: 用户备注（可选）

    **业务逻辑：**
    1. 验证所有商品存在且上架
    2. 检查每件商品库存是否充足
    3. 计算订单总价
    4. 创建多个订单记录（每件商品一个订单）
    5. 批量扣减商品库存

    **注意：**
    - 支持一次购买多个不同商品
    - 每件商品生成独立的订单
    - 所有商品必须同时满足购买条件
    """,
    responses={
        200: {"description": "批量订单创建成功"},
        400: {"description": "商品不存在、库存不足或数据无效"},
        401: {"description": "未认证"}
    }
)
async def create_cart_order(
    items: List[CartItem],
    payment_method: str = Query("balance", description="支付方式"),
    user_note: Optional[str] = Query(None, description="用户备注"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """从购物车创建订单"""
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="购物车为空"
        )

    total_amount = 0.0
    order_items = []

    for item in items:
        # 验证商品
        from app.services.product import product_service
        product = await product_service.get_product_by_id(db, item.product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {item.product_id} 不存在或已下架"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 库存不足"
            )

        item_total = float(product.price * item.quantity)
        total_amount += item_total

        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return OrderSummary(
        items=items,
        total_amount=total_amount
    )


@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新订单"""
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限
    if not current_user.is_superuser and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此订单"
        )

    # 只有管理员可以修改订单状态
    if order_in.status and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改订单状态"
        )

    try:
        updated_order = await order_service.update_order(db, order, order_in)
        return updated_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/pay", response_model=OrderSchema)
async def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """支付订单"""
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权支付此订单"
        )

    try:
        paid_order = await order_service.pay_order(db, order, current_user)
        return paid_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/deliver")
async def deliver_order(
    order_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """发货订单（管理员）"""
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    try:
        delivered_order = await order_service.deliver_order(db, order)
        return {
            "message": "订单已发货",
            "delivery_content": delivered_order.delivery_content
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/cancel", response_model=OrderSchema)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限
    if not current_user.is_superuser and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消此订单"
        )

    try:
        cancelled_order = await order_service.cancel_order(db, order)
        return cancelled_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/refund")
async def refund_order(
    order_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """退款订单（管理员）"""
    order = await order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    try:
        refunded_order = await order_service.refund_order(db, order)
        return {"message": "订单已退款"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

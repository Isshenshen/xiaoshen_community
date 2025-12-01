"""
卡密管理API

提供卡密信息的完整CRUD管理功能，包括：
- 卡密查询和筛选
- 卡密创建和批量导入
- 卡密状态管理（锁定/解锁）
- 卡密删除和清理
- 卡密使用统计

权限说明：
- 仅管理员可以访问所有卡密管理功能
- 普通用户无法查看卡密信息

安全考虑：
- 卡密内容经过加密存储
- 只有管理员可以查看明文卡密
- 卡密一旦使用即不可逆转
- 支持卡密过期机制

业务规则：
- 新创建的卡密默认为未使用状态
- 卡密可以被锁定以防止误发
- 支持批量导入提高效率
- 卡密过期后自动变为无效状态
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_superuser
from app.models.user import User
from app.schemas.card import (
    Card as CardSchema,
    CardCreate,
    CardUpdate,
    CardList,
    CardBatchCreate
)
from app.services.card import card_service

# 创建卡密管理路由器
router = APIRouter(
    prefix="/cards",  # 路由前缀
    tags=["卡密管理"]  # API文档分组标签
)


@router.get(
    "/",
    response_model=CardList,
    summary="获取卡密列表",
    description="""
    获取卡密列表，支持多条件筛选和分页。

    **查询参数：**
    - `product_id`: 商品ID筛选
    - `status`: 卡密状态筛选
      - `unused`: 未使用
      - `used`: 已使用
      - `locked`: 已锁定
      - `expired`: 已过期
    - `skip`: 跳过的记录数（分页）
    - `limit`: 返回记录数（1-100）

    **返回信息：**
    - 卡密基本信息（ID、商品ID、状态等）
    - 卡密内容（加密显示）
    - 使用信息（使用者、时间）
    - 过期时间

    **权限：** 仅管理员可访问
    """,
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未认证"},
        403: {"description": "权限不足"}
    }
)
async def read_cards(
    product_id: Optional[int] = Query(None, description="商品ID筛选"),
    status: Optional[str] = Query(None, description="卡密状态筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取卡密列表（管理员）"""
    from app.models.card import CardStatus

    card_status = None
    if status:
        try:
            card_status = CardStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的卡密状态"
            )

    cards = await card_service.get_cards(
        db,
        product_id=product_id,
        status=card_status,
        skip=skip,
        limit=limit
    )

    # 获取总数（简化版）
    total = len(cards) if len(cards) < limit else skip + limit + 1

    return CardList(
        items=cards,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{card_id}", response_model=CardSchema)
async def read_card(
    card_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取卡密详情（管理员）"""
    card = await card_service.get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )
    return card


@router.post("/", response_model=CardSchema)
async def create_card(
    card_in: CardCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """创建卡密（管理员）"""
    try:
        card = await card_service.create_card(db, card_in)
        return card
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/batch", response_model=List[CardSchema])
async def batch_create_cards(
    batch_in: CardBatchCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """批量创建卡密（管理员）"""
    try:
        cards = await card_service.batch_create_cards(db, batch_in)
        return cards
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{card_id}", response_model=CardSchema)
async def update_card(
    card_id: int,
    card_in: CardUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """更新卡密（管理员）"""
    card = await card_service.get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )

    try:
        updated_card = await card_service.update_card(db, card, card_in)
        return updated_card
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """删除卡密（管理员）"""
    card = await card_service.get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )

    if card.status == "used":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已使用的卡密不能删除"
        )

    await card_service.delete_card(db, card)
    return {"message": "卡密已删除"}


@router.post("/{card_id}/lock")
async def lock_card(
    card_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """锁定卡密（管理员）"""
    card = await card_service.get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )

    if card.status == "used":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已使用的卡密不能锁定"
        )

    await card_service.lock_card(db, card)
    return {"message": "卡密已锁定"}


@router.post("/{card_id}/unlock")
async def unlock_card(
    card_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """解锁卡密（管理员）"""
    card = await card_service.get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )

    if card.status != "locked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有锁定的卡密才能解锁"
        )

    await card_service.unlock_card(db, card)
    return {"message": "卡密已解锁"}

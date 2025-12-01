"""
用户管理API

提供用户信息的查询、更新和管理功能，包括：
- 当前用户信息管理
- 用户资料更新
- 用户余额管理
- 管理员用户列表管理

权限说明：
- 普通用户：只能管理自己的信息
- 管理员：可以查看和管理所有用户

安全考虑：
- 密码等敏感信息不会在API中返回
- 用户更新需要验证权限
- 敏感操作需要管理员权限
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_active_superuser
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.user import user_service

# 创建用户管理路由器
router = APIRouter(
    tags=["用户管理"]  # API文档分组标签
)


@router.get(
    "/me",
    response_model=UserSchema,
    summary="获取当前用户信息",
    description="""
    获取当前登录用户的详细信息。

    **返回信息：**
    - 用户ID、用户名、邮箱
    - 注册时间、最后登录时间
    - 账户余额、用户状态等

    **注意：** 不包含密码等敏感信息
    """,
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未认证"}
    }
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    从JWT令牌中解析出用户信息并返回，
    不访问数据库，直接返回已认证的用户对象。

    Args:
        current_user: 通过依赖注入获取的当前用户

    Returns:
        UserSchema: 当前用户信息
    """
    return current_user


@router.put(
    "/me",
    response_model=UserSchema,
    summary="更新当前用户信息",
    description="""
    更新当前登录用户的个人信息。

    **可更新字段：**
    - `email`: 邮箱地址
    - `full_name`: 真实姓名
    - `phone`: 手机号

    **注意：**
    - 用户名不可修改
    - 邮箱格式会进行验证
    - 手机号格式会进行验证
    """,
    responses={
        200: {"description": "更新成功"},
        400: {"description": "数据格式错误"},
        401: {"description": "未认证"}
    }
)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息

    支持部分更新，只更新提供的字段。
    验证邮箱和手机号等数据的有效性。

    Args:
        user_in: 用户更新数据
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        UserSchema: 更新后的用户信息

    Raises:
        HTTPException: 当数据格式错误时抛出400错误
    """
    try:
        user = await user_service.update(db, current_user, user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/balance")
async def get_user_balance(current_user: User = Depends(get_current_user)):
    """获取用户余额"""
    return {"balance": current_user.balance}


@router.post("/recharge")
async def recharge_balance(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """充值余额"""
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="充值金额必须大于0"
        )

    user = await user_service.update_balance(db, current_user, amount)
    return {"message": "充值成功", "balance": user.balance}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    from app.core.security import verify_password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )

    await user_service.change_password(db, current_user, new_password)
    return {"message": "密码修改成功"}


# 管理员专用API
@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（管理员）"""
    from sqlalchemy import select
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取指定用户信息（管理员）"""
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息（管理员）"""
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    try:
        updated_user = await user_service.update(db, user, user_in)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """删除用户（管理员）"""
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )

    # 软删除：设置为非活跃状态
    user.is_active = False
    await db.commit()

    return {"message": "用户已禁用"}

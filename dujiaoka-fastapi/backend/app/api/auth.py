"""
认证相关API

提供用户认证、注册、登录、用户信息管理等核心认证功能。

主要功能：
- 用户注册
- 用户登录
- 获取当前用户信息
- 更新用户信息
- 修改密码

依赖关系：
- 通过JWT token进行身份验证
- 使用bcrypt进行密码加密
- 依赖用户服务层进行业务逻辑处理
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, Token, User
from app.services.user import user_service

# 创建认证路由器
router = APIRouter(
    tags=["认证"]  # API文档分组标签
)


@router.post(
    "/register",
    response_model=User,
    summary="用户注册",
    description="""
    创建新用户账户。

    **输入参数：**
    - `username`: 用户名（必填，3-20字符）
    - `email`: 邮箱地址（必填，格式验证）
    - `password`: 密码（必填，6位以上）
    - `full_name`: 真实姓名（可选）
    - `phone`: 手机号（可选）

    **返回：** 新创建的用户信息（不含密码）

    **错误：**
    - 400: 用户名或邮箱已存在，数据格式错误
    """,
    responses={
        200: {"description": "注册成功"},
        400: {"description": "注册失败，用户名或邮箱已存在"}
    }
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册接口

    验证用户输入数据，检查用户名和邮箱唯一性，
    创建新用户账户并返回用户信息。

    Args:
        user_in: 用户注册数据
        db: 数据库会话

    Returns:
        User: 创建成功的用户信息

    Raises:
        HTTPException: 当用户名或邮箱已存在时抛出400错误
    """
    try:
        # 调用用户服务创建用户
        user = await user_service.create(db, user_in)
        return user
    except ValueError as e:
        # 处理业务逻辑错误（如用户名重复）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="""
    用户登录获取访问令牌。

    **支持的登录方式：**
    - 用户名 + 密码
    - 邮箱 + 密码

    **请求参数：**
    - `username`: 用户名或邮箱地址
    - `password`: 用户密码

    **返回：**
    - `access_token`: JWT访问令牌
    - `token_type`: 令牌类型（bearer）

    **使用方法：**
    在后续API请求的Authorization头中使用：
    `Authorization: Bearer {access_token}`

    **令牌有效期：** 8天
    """,
)
async def login(
    username: str = Form(..., description="用户名或邮箱"),
    password: str = Form(..., description="密码"),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口

    支持用户名或邮箱登录，验证密码正确性，
    生成并返回JWT访问令牌。

    登录流程：
    1. 接收用户名和密码
    2. 验证用户身份
    3. 生成访问令牌
    4. 返回令牌信息

    Args:
        username: 用户名或邮箱地址
        password: 用户密码
        db: 数据库会话

    Returns:
        Token: 包含访问令牌的响应

    Raises:
        HTTPException: 当用户名或密码错误时抛出401错误
    """
    # 验证用户身份
    user = await user_service.authenticate(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},  # 标准OAuth2响应头
        )

    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username,  # 使用用户名作为token主题
        expires_delta=access_token_expires
    )

    # 返回标准OAuth2令牌响应
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=User,
    summary="获取当前用户信息",
    description="""
    获取当前登录用户的基本信息。

    **需要认证：** 请求头中必须包含有效的JWT令牌

    **返回信息：**
    - 用户ID、用户名、邮箱
    - 注册时间、最后登录时间
    - 账户余额、用户状态等
    """,
    responses={
        200: {"description": "获取成功"},
        401: {"description": "未认证或令牌无效"}
    }
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息

    从JWT令牌中解析出用户信息并返回，
    不访问数据库，直接返回已认证的用户对象。

    Args:
        current_user: 通过依赖注入获取的当前用户

    Returns:
        User: 当前用户信息
    """
    return current_user


@router.put(
    "/me",
    response_model=User,
    summary="更新当前用户信息",
    description="""
    更新当前登录用户的个人信息。

    **可更新字段：**
    - `email`: 邮箱地址
    - `full_name`: 真实姓名
    - `phone`: 手机号

    **注意：** 用户名不可修改，如需修改请联系管理员
    """,
    responses={
        200: {"description": "更新成功"},
        400: {"description": "数据格式错误"},
        401: {"description": "未认证"}
    }
)
async def update_user_me(
    user_in: dict,  # 使用dict以便部分更新
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息

    支持部分更新，只更新提供的字段。
    验证邮箱格式等数据有效性。

    Args:
        user_in: 要更新的用户数据字典
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        User: 更新后的用户信息

    Raises:
        HTTPException: 当数据格式错误时抛出400错误
    """
    try:
        from app.schemas.user import UserUpdate
        # 转换为Pydantic模型进行验证
        user_update = UserUpdate(**user_in)
        # 调用服务层更新用户信息
        user = await user_service.update(db, current_user, user_update)
        return user
    except ValueError as e:
        # 处理数据验证错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/change-password",
    summary="修改密码",
    description="""
    修改当前用户的登录密码。

    **安全要求：**
    - 必须提供当前密码进行验证
    - 新密码长度至少6位
    - 新密码不能与旧密码相同

    **注意：**
    修改密码后，旧的JWT令牌仍然有效，
    建议重新登录获取新的令牌。
    """,
    responses={
        200: {"description": "密码修改成功"},
        400: {"description": "旧密码错误或新密码不符合要求"},
        401: {"description": "未认证"}
    }
)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改用户密码

    安全地修改用户密码，需要验证旧密码正确性。
    新密码会通过bcrypt进行加密存储。

    密码修改流程：
    1. 验证旧密码正确性
    2. 验证新密码格式
    3. 加密新密码并更新数据库
    4. 返回成功响应

    Args:
        old_password: 当前密码（用于验证）
        new_password: 新密码
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        dict: 成功消息

    Raises:
        HTTPException: 当旧密码错误时抛出400错误
    """
    # 验证旧密码正确性
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )

    # 更新密码（服务层会处理密码验证和加密）
    await user_service.change_password(db, current_user, new_password)

    return {"message": "密码修改成功"}

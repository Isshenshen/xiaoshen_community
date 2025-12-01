"""
用户服务层
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """用户服务"""

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if await self.get_by_username(db, user_in.username):
            raise ValueError("Username already exists")

        # 检查邮箱是否已存在
        if await self.get_by_email(db, user_in.email):
            raise ValueError("Email already exists")

        # 创建用户
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            phone=user_in.phone,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, user: User, user_in: UserUpdate) -> User:
        """更新用户信息"""
        # 检查邮箱是否已被其他用户使用
        if user_in.email and user_in.email != user.email:
            if await self.get_by_email(db, user_in.email):
                raise ValueError("Email already exists")

        # 更新字段
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()

        return user

    async def change_password(self, db: AsyncSession, user: User, new_password: str) -> User:
        """修改密码"""
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    async def update_balance(self, db: AsyncSession, user: User, amount: float) -> User:
        """更新用户余额"""
        user.balance += amount
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user


# 创建服务实例
user_service = UserService()

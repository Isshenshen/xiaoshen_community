"""
数据库配置和连接
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy基础模型"""
    pass


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace("mysql+mysqlconnector://", "mysql+aiomysql://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=StaticPool,
)


# 创建异步会话工厂
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

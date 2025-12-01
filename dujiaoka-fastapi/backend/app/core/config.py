"""
核心配置文件
支持环境变量和 .env 文件配置
"""
import secrets
import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 项目基本信息
    PROJECT_NAME: str = "小申交流站"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 安全设置
    # 生产环境必须通过环境变量设置 SECRET_KEY
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        secrets.token_urlsafe(32) if os.getenv("DEBUG", "true").lower() == "true" else ""
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天

    # 数据库设置
    # 开发环境默认使用 SQLite，生产环境推荐 PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./dujiaoka_fastapi.db"

    # Redis 设置（可选，用于缓存和会话）
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # CORS 设置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Vue 开发服务器
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # 允许的主机
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # 调试模式
    DEBUG: bool = True

    # 支付配置
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None

    WECHAT_APP_ID: Optional[str] = None
    WECHAT_MCH_ID: Optional[str] = None
    WECHAT_PRIVATE_KEY: Optional[str] = None

    # 文件上传设置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 卡密加密密钥 (32字节 base64 编码)
    CARD_ENCRYPTION_KEY: str = "your-card-encryption-key-32-chars-minimum"

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """验证 SECRET_KEY 在生产环境中已正确设置"""
        debug = os.getenv("DEBUG", "true").lower() == "true"
        if not debug and (not v or len(v) < 32):
            raise ValueError(
                "生产环境必须设置 SECRET_KEY 环境变量（至少 32 个字符）"
            )
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """组装 CORS origins"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """组装允许的主机"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()

# 启动时安全检查
if not settings.DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    
    # 检查 SECRET_KEY
    if settings.SECRET_KEY == "your-super-secret-key-change-this-in-production-must-be-at-least-32-chars":
        logger.warning("⚠️ 警告: 请修改 SECRET_KEY 为安全的随机值！")
    
    # 检查 CARD_ENCRYPTION_KEY
    if settings.CARD_ENCRYPTION_KEY == "your-card-encryption-key-32-chars-minimum":
        logger.warning("⚠️ 警告: 请修改 CARD_ENCRYPTION_KEY 为安全的随机值！")
    
    # 检查数据库
    if "sqlite" in settings.DATABASE_URL.lower():
        logger.warning("⚠️ 警告: 生产环境建议使用 PostgreSQL 而非 SQLite！")

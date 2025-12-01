"""
小申交流站 - 分享学习，共同成长
"""
import os
import uvicorn

# 设置默认的卡密加密密钥（如果环境变量未设置）
if 'CARD_ENCRYPTION_KEY' not in os.environ or len(os.environ.get('CARD_ENCRYPTION_KEY', '')) < 32:
    os.environ['CARD_ENCRYPTION_KEY'] = 'dGVzdC1rZXktZm9yLWRlamlhLWthLWZhc3RhcGktMzItYnl0ZXM='

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.database import create_tables

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="小申交流站 - 分享学习资源，技术交流，共同成长",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 设置 CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 设置可信主机（生产环境）
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    
    # 生产环境不暴露详细错误信息
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "服务器内部错误"
    
    return JSONResponse(
        status_code=500,
        content={"detail": detail}
    )

# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("=" * 50)
    logger.info(f"🚀 {settings.PROJECT_NAME} 启动中...")
    logger.info(f"📌 版本: {settings.VERSION}")
    logger.info(f"🔧 调试模式: {settings.DEBUG}")
    logger.info("=" * 50)
    
    # 创建数据库表
    await create_tables()
    logger.info("✅ 数据库表初始化完成")
    
    # 生产环境安全检查
    if not settings.DEBUG:
        logger.info("🔒 生产环境安全检查...")
        if "sqlite" in settings.DATABASE_URL.lower():
            logger.warning("⚠️ 生产环境建议使用 PostgreSQL！")
        logger.info("✅ 安全检查完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("👋 应用关闭中...")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG,
    )

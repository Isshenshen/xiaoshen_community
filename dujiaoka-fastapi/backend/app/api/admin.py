"""
后台管理API
"""
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.dependencies import get_current_active_superuser
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.payment import Payment, PaymentStatus

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取仪表盘统计数据"""
    # 计算时间范围
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {}

    # 用户统计
    user_result = await db.execute(select(func.count(User.id)))
    stats["total_users"] = user_result.scalar()

    # 新用户统计
    new_users_today = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )
    stats["new_users_today"] = new_users_today.scalar()

    new_users_week = await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) >= week_ago
        )
    )
    stats["new_users_week"] = new_users_week.scalar()

    # 订单统计
    order_result = await db.execute(select(func.count(Order.id)))
    stats["total_orders"] = order_result.scalar()

    # 今日订单
    orders_today = await db.execute(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
    )
    stats["orders_today"] = orders_today.scalar()

    # 订单金额统计
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount))
    )
    stats["total_revenue"] = float(revenue_result.scalar() or 0)

    revenue_today = await db.execute(
        select(func.sum(Order.total_amount)).where(
            func.date(Order.created_at) == today
        )
    )
    stats["revenue_today"] = float(revenue_today.scalar() or 0)

    # 订单状态统计
    order_status_stats = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    stats["order_status"] = {status.value: count for status, count in order_status_stats}

    # 商品统计
    product_result = await db.execute(select(func.count(Product.id)))
    stats["total_products"] = product_result.scalar()

    active_products = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    stats["active_products"] = active_products.scalar()

    # 支付统计
    payment_result = await db.execute(select(func.count(Payment.id)))
    stats["total_payments"] = payment_result.scalar()

    successful_payments = await db.execute(
        select(func.count(Payment.id)).where(Payment.status == PaymentStatus.SUCCESS)
    )
    stats["successful_payments"] = successful_payments.scalar()

    return stats


@router.get("/dashboard/charts")
async def get_dashboard_charts(
    days: int = 30,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取仪表盘图表数据"""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    # 每日订单数量
    daily_orders = await db.execute(
        select(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        )
        .where(func.date(Order.created_at) >= start_date)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )

    order_chart = [
        {"date": str(date), "orders": count}
        for date, count in daily_orders
    ]

    # 每日收入
    daily_revenue = await db.execute(
        select(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        )
        .where(
            and_(
                func.date(Order.created_at) >= start_date,
                Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED])
            )
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )

    revenue_chart = [
        {"date": str(date), "revenue": float(revenue or 0)}
        for date, revenue in daily_revenue
    ]

    # 商品销量排行
    product_sales = await db.execute(
        select(
            Product.name,
            func.sum(Order.quantity).label('sold_quantity'),
            func.sum(Order.total_amount).label('total_revenue')
        )
        .join(Order, Product.id == Order.product_id)
        .where(
            and_(
                func.date(Order.created_at) >= start_date,
                Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED])
            )
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(Order.total_amount).desc())
        .limit(10)
    )

    sales_chart = [
        {
            "product": name,
            "quantity": int(quantity),
            "revenue": float(revenue or 0)
        }
        for name, quantity, revenue in product_sales
    ]

    return {
        "order_chart": order_chart,
        "revenue_chart": revenue_chart,
        "sales_chart": sales_chart
    }


@router.get("/system/info")
async def get_system_info(
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取系统信息"""
    # 数据库表统计
    tables_info = {}

    # 用户表
    user_count = await db.execute(select(func.count(User.id)))
    tables_info["users"] = user_count.scalar()

    # 商品表
    product_count = await db.execute(select(func.count(Product.id)))
    tables_info["products"] = product_count.scalar()

    # 订单表
    order_count = await db.execute(select(func.count(Order.id)))
    tables_info["orders"] = order_count.scalar()

    # 支付表
    payment_count = await db.execute(select(func.count(Payment.id)))
    tables_info["payments"] = payment_count.scalar()

    return {
        "database_tables": tables_info,
        "server_time": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

#!/usr/bin/env python3
"""
数据初始化脚本
用于创建示例数据，方便测试和演示
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.product import Product, Category
from app.models.card import Card
from app.services.user import user_service
from app.services.product import product_service


async def create_sample_data():
    """创建示例数据"""
    from app.core.database import async_session_maker
    db = async_session_maker()
    try:
        print("🔄 开始初始化示例数据...")

        # 1. 创建管理员用户
        print("👤 创建管理员用户...")
        # 检查用户是否已存在
        existing_admin = await user_service.get_by_username(db, "admin")
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                is_superuser=True,
                is_active=True,
                balance=1000.0
            )
            db.add(admin_user)
            print("  - 创建管理员用户")
        else:
            print("  - 管理员用户已存在，跳过")

        # 创建普通用户
        existing_user = await user_service.get_by_username(db, "user1")
        if not existing_user:
            regular_user = User(
                username="user1",
                email="user1@example.com",
                hashed_password=get_password_hash("user123"),
                full_name="测试用户",
                is_superuser=False,
                is_active=True,
                balance=500.0
            )
            db.add(regular_user)
            print("  - 创建普通用户")
        else:
            print("  - 普通用户已存在，跳过")

        await db.commit()
        print("✅ 用户创建完成")

        # 2. 创建商品分类
        print("📂 创建商品分类...")
        categories_data = [
            ("Web开发", "网站开发相关源码"),
            ("移动开发", "移动应用开发源码"),
            ("桌面应用", "桌面应用程序源码"),
            ("工具脚本", "实用工具和脚本"),
        ]

        for i, (name, description) in enumerate(categories_data):
            try:
                category = Category(
                    name=name,
                    description=description,
                    sort_order=i + 1,
                    is_active=True
                )
                db.add(category)
                await db.commit()
                print(f"  - 创建分类: {name}")
            except Exception as e:
                # 分类可能已存在，跳过
                await db.rollback()
                print(f"  - 分类已存在: {name}")

        print("✅ 分类创建完成")

        # 3. 创建示例商品
        print("📦 创建示例商品...")
        products_data = [
            ("Vue3 + FastAPI全栈电商平台", "基于Vue3和FastAPI的全栈电商平台，包含用户管理、商品展示、购物车、订单系统等完整功能。支持支付宝、微信支付。", 299.0, 399.0, 1, "/api/static/images/product1.jpg"),
            ("React Native移动商城APP", "完整的React Native移动商城应用，支持iOS和Android双平台。包含商品浏览、购物车、订单管理、支付集成等功能。", 399.0, 599.0, 2, "/api/static/images/product2.jpg"),
            ("Python自动化办公工具集", "包含Excel处理、PDF生成、邮件发送、文件批量处理等办公自动化脚本。支持一键安装和使用。", 99.0, 149.0, 4, "/api/static/images/product3.jpg"),
            ("Electron桌面记事本应用", "基于Electron开发的现代化桌面记事本应用，支持Markdown编辑、富文本格式、本地存储、数据同步等功能。", 149.0, 199.0, 3, "/api/static/images/product4.jpg"),
            ("Django REST API后端框架", "基于Django REST Framework的完整后端API框架，包含用户认证、权限管理、数据序列化、API文档等核心功能。", 199.0, 299.0, 1, "/api/static/images/product5.jpg"),
            ("Flutter跨平台商城应用", "使用Flutter开发的跨平台商城应用，一套代码同时支持iOS、Android、Web等多个平台。包含完整的电商功能。", 349.0, 499.0, 2, "/api/static/images/product6.jpg"),
        ]

        for i, (name, desc, price, orig_price, cat_id, img_url) in enumerate(products_data):
            try:
                product = Product(
                    name=name,
                    description=desc,
                    price=price,
                    original_price=orig_price,
                    category_id=cat_id,
                    stock=50 - i * 5,  # 递减库存
                    sold_count=23 - i * 3,  # 递减销量
                    auto_delivery=True,
                    is_active=True,
                    sort_order=i + 1,
                    image_url=img_url
                )
                db.add(product)
                await db.commit()
                print(f"  - 创建商品: {name}")
            except Exception as e:
                await db.rollback()
                print(f"  - 商品已存在: {name}")

        print("✅ 商品创建完成")

        # 4. 创建示例卡密（用于测试自动发货）
        print("🎫 创建示例卡密...")
        card_data = [
            (1, "VUE3-FASTAPI-2024-001"),
            (1, "VUE3-FASTAPI-2024-002"),
            (2, "RN-MALL-2024-001"),
            (3, "PYTHON-TOOLS-2024-001"),
            (4, "ELECTRON-NOTES-2024-001"),
        ]

        for product_id, secret in card_data:
            try:
                card = Card(
                    product_id=product_id,
                    card_secret=secret,
                    status="unused",
                    encrypted_content=secret,  # 暂时使用明文作为加密内容
                    expires_at=None
                )
                db.add(card)
                await db.commit()
                print(f"  - 创建卡密: {secret}")
            except Exception as e:
                await db.rollback()
                print(f"  - 卡密已存在: {secret}")

        print("✅ 卡密创建完成")

        print("\n🎉 示例数据初始化完成！")
        print("\n📋 默认账号信息：")
        print("管理员账号: admin / admin123")
        print("普通用户: user1 / user123")
        print("\n🚀 现在可以启动服务进行测试了！")
    except Exception as e:
        print(f"❌ 初始化数据失败: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


async def main():
    """主函数"""
    print("🌱 CodeHub 示例数据初始化工具")
    print("=" * 40)

    # 检查是否已经初始化过
    async for db in get_db():
        try:
            result = await db.execute("SELECT COUNT(*) FROM users")
            count = result.scalar()
            if count > 0:
                print("⚠️  数据库中已有数据，跳过初始化")
                print("如果需要重新初始化，请先清空数据库")
                return
        except Exception:
            # 表不存在，继续初始化
            pass

    await create_sample_data()


if __name__ == "__main__":
    asyncio.run(main())

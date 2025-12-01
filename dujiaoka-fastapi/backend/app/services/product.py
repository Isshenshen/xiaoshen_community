"""
商品服务层
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.product import Product, Category
from app.schemas.product import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate


class ProductService:
    """商品服务"""

    async def get_categories(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
        """获取分类列表"""
        result = await db.execute(
            select(Category)
            .where(Category.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Category.sort_order, Category.created_at.desc())
        )
        return result.scalars().all()

    async def get_category_by_id(self, db: AsyncSession, category_id: int) -> Optional[Category]:
        """根据ID获取分类"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalars().first()

    async def create_category(self, db: AsyncSession, category_in: CategoryCreate) -> Category:
        """创建分类"""
        category = Category(**category_in.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    async def update_category(self, db: AsyncSession, category: Category, category_in: CategoryUpdate) -> Category:
        """更新分类"""
        update_data = category_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        await db.commit()
        await db.refresh(category)
        return category

    async def delete_category(self, db: AsyncSession, category: Category) -> None:
        """删除分类"""
        category.is_active = False
        await db.commit()

    async def get_products(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Product]:
        """获取商品列表"""
        query = select(Product).options(selectinload(Product.category))

        # 构建过滤条件
        conditions = []
        if category_id:
            conditions.append(Product.category_id == category_id)
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        if search:
            conditions.append(
                or_(
                    Product.name.contains(search),
                    Product.description.contains(search)
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(
            Product.sort_order, Product.created_at.desc()
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def get_product_by_id(self, db: AsyncSession, product_id: int) -> Optional[Product]:
        """根据ID获取商品"""
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        return result.scalars().first()

    async def create_product(self, db: AsyncSession, product_in: ProductCreate) -> Product:
        """创建商品"""
        # 检查分类是否存在
        if product_in.category_id:
            category = await self.get_category_by_id(db, product_in.category_id)
            if not category:
                raise ValueError("分类不存在")

        product = Product(**product_in.model_dump())
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    async def update_product(self, db: AsyncSession, product: Product, product_in: ProductUpdate) -> Product:
        """更新商品"""
        # 检查分类是否存在
        if product_in.category_id:
            category = await self.get_category_by_id(db, product_in.category_id)
            if not category:
                raise ValueError("分类不存在")

        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        await db.commit()
        await db.refresh(product)
        return product

    async def delete_product(self, db: AsyncSession, product: Product) -> None:
        """删除商品"""
        product.is_active = False
        await db.commit()

    async def update_stock(self, db: AsyncSession, product: Product, quantity: int) -> Product:
        """更新商品库存"""
        if product.stock + quantity < 0:
            raise ValueError("库存不足")

        product.stock += quantity
        await db.commit()
        await db.refresh(product)
        return product

    async def increment_sold_count(self, db: AsyncSession, product: Product, quantity: int = 1) -> Product:
        """增加商品销量"""
        product.sold_count += quantity
        await db.commit()
        await db.refresh(product)
        return product


# 创建服务实例
product_service = ProductService()

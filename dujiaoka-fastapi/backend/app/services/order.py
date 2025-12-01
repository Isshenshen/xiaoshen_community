"""
订单服务层
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus, PaymentMethod
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, CartItem
from app.services.product import product_service
# from app.services.card import card_service  # 卡密功能已禁用
from app.services.user import user_service


class OrderService:
    """订单服务"""

    async def get_orders(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """获取订单列表"""
        query = (
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.product)
            )
        )

        conditions = []
        if user_id:
            conditions.append(Order.user_id == user_id)
        if status:
            conditions.append(Order.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(desc(Order.created_at))

        result = await db.execute(query)
        return result.scalars().all()

    async def get_order_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.product)
            )
            .where(Order.id == order_id)
        )
        return result.scalars().first()

    async def get_order_by_number(self, db: AsyncSession, order_number: str) -> Optional[Order]:
        """根据订单号获取订单"""
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.product)
            )
            .where(Order.order_number == order_number)
        )
        return result.scalars().first()

    async def create_order(self, db: AsyncSession, order_in: OrderCreate, user: User) -> Order:
        """创建订单"""
        # 获取商品信息
        product = await product_service.get_product_by_id(db, order_in.product_id)
        if not product:
            raise ValueError("商品不存在")

        if not product.is_active:
            raise ValueError("商品已下架")

        if product.stock < order_in.quantity:
            raise ValueError("商品库存不足")

        # 计算总金额
        total_amount = float(product.price * order_in.quantity)

        # 生成订单号
        order_number = self.generate_order_number()

        # 创建订单
        order = Order(
            order_number=order_number,
            user_id=user.id,
            product_id=order_in.product_id,
            product_name=product.name,
            product_price=product.price,
            quantity=order_in.quantity,
            total_amount=total_amount,
            payment_method=order_in.payment_method,
            user_note=order_in.user_note,
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def update_order(self, db: AsyncSession, order: Order, order_in: OrderUpdate) -> Order:
        """更新订单"""
        update_data = order_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        await db.commit()
        await db.refresh(order)
        return order

    async def pay_order(self, db: AsyncSession, order: Order, user: User) -> Order:
        """支付订单"""
        if order.status != OrderStatus.PENDING:
            raise ValueError("订单状态不允许支付")

        if order.payment_method == PaymentMethod.BALANCE:
            # 余额支付
            if user.balance < order.total_amount:
                raise ValueError("余额不足")

            # 扣除余额
            await user_service.update_balance(db, user, -order.total_amount)

            # 更新订单状态
            order.status = OrderStatus.PAID
            order.paid_at = datetime.utcnow()

            # 自动发卡
            await self.deliver_order(db, order)

        else:
            # 第三方支付，标记为已支付（实际应该在支付回调中处理）
            order.status = OrderStatus.PAID
            order.paid_at = datetime.utcnow()
            await self.deliver_order(db, order)

        await db.commit()
        await db.refresh(order)
        return order

    async def deliver_order(self, db: AsyncSession, order: Order) -> Order:
        """发货订单"""
        if order.status != OrderStatus.PAID:
            raise ValueError("订单未支付")

        # 获取商品
        product = await product_service.get_product_by_id(db, order.product_id)
        if not product:
            raise ValueError("商品不存在")

        if not product.auto_delivery:
            # 手动发货
            order.status = OrderStatus.DELIVERED
            order.delivered_at = datetime.utcnow()
            await db.commit()
            return order

        # 源码项目自动发货
        delivery_content = f"""
感谢购买！您的源码项目已准备就绪。

项目信息：
- 商品名称: {product.name}
- 购买数量: {order.quantity}
- 订单号: {order.order_number}

下载链接将在订单完成后提供。
客服QQ: 123456789
"""

        # 更新订单
        order.status = OrderStatus.DELIVERED
        order.delivery_content = delivery_content.strip()
        order.delivered_at = datetime.utcnow()

        # 减少商品库存
        await product_service.update_stock(db, product, -order.quantity)

        # 增加商品销量
        await product_service.increment_sold_count(db, product, order.quantity)

        await db.commit()
        await db.refresh(order)
        return order

    async def cancel_order(self, db: AsyncSession, order: Order) -> Order:
        """取消订单"""
        if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            raise ValueError("订单状态不允许取消")

        # 如果已支付，退还余额
        if order.status == OrderStatus.PAID and order.payment_method == PaymentMethod.BALANCE:
            user = await user_service.get_by_id(db, order.user_id)
            if user:
                await user_service.update_balance(db, user, order.total_amount)

        order.status = OrderStatus.CANCELLED
        await db.commit()
        await db.refresh(order)
        return order

    async def refund_order(self, db: AsyncSession, order: Order) -> Order:
        """退款订单"""
        if order.status != OrderStatus.DELIVERED:
            raise ValueError("订单状态不允许退款")

        # 退还余额
        if order.payment_method == PaymentMethod.BALANCE:
            user = await user_service.get_by_id(db, order.user_id)
            if user:
                await user_service.update_balance(db, user, order.total_amount)

        order.status = OrderStatus.REFUNDED
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    def generate_order_number() -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(datetime.now().microsecond)[:3]
        return f"ORD{timestamp}{random_str}"


# 创建服务实例
order_service = OrderService()

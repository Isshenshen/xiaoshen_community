"""
支付服务层
"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.models.payment import Payment, PaymentStatus
from app.models.order import Order
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentService:
    """支付服务"""

    async def get_payments(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        order_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """获取支付记录列表"""
        query = (
            select(Payment)
            .options(
                selectinload(Payment.user),
                selectinload(Payment.order)
            )
        )

        conditions = []
        if user_id:
            conditions.append(Payment.user_id == user_id)
        if order_id:
            conditions.append(Payment.order_id == order_id)
        if status:
            conditions.append(Payment.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(desc(Payment.created_at))

        result = await db.execute(query)
        return result.scalars().all()

    async def get_payment_by_id(self, db: AsyncSession, payment_id: int) -> Optional[Payment]:
        """根据ID获取支付记录"""
        result = await db.execute(
            select(Payment)
            .options(
                selectinload(Payment.user),
                selectinload(Payment.order)
            )
            .where(Payment.id == payment_id)
        )
        return result.scalars().first()

    async def get_payment_by_transaction_id(
        self,
        db: AsyncSession,
        transaction_id: str
    ) -> Optional[Payment]:
        """根据交易号获取支付记录"""
        result = await db.execute(
            select(Payment)
            .options(
                selectinload(Payment.user),
                selectinload(Payment.order)
            )
            .where(Payment.transaction_id == transaction_id)
        )
        return result.scalars().first()

    async def create_payment(self, db: AsyncSession, payment_in: PaymentCreate) -> Payment:
        """创建支付记录"""
        # 检查用户是否存在
        result = await db.execute(select(User).where(User.id == payment_in.user_id))
        user = result.scalars().first()
        if not user:
            raise ValueError("用户不存在")

        # 检查订单是否存在
        result = await db.execute(select(Order).where(Order.id == payment_in.order_id))
        order = result.scalars().first()
        if not order:
            raise ValueError("订单不存在")

        payment = Payment(
            user_id=payment_in.user_id,
            order_id=payment_in.order_id,
            payment_method=payment_in.payment_method,
            amount=payment_in.amount,
            status=PaymentStatus.PENDING,
        )

        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment

    async def update_payment(
        self,
        db: AsyncSession,
        payment: Payment,
        payment_in: PaymentUpdate
    ) -> Payment:
        """更新支付记录"""
        update_data = payment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)

        # 如果状态更新为成功，设置支付时间
        if payment_in.status == PaymentStatus.SUCCESS and payment.status != PaymentStatus.SUCCESS:
            payment.paid_at = datetime.utcnow()

        await db.commit()
        await db.refresh(payment)
        return payment

    async def handle_alipay_callback(self, db: AsyncSession, callback_data: dict) -> dict:
        """处理支付宝回调"""
        # 验证回调数据
        out_trade_no = callback_data.get("out_trade_no")
        trade_no = callback_data.get("trade_no")
        total_amount = callback_data.get("total_amount")
        trade_status = callback_data.get("trade_status")

        if not out_trade_no or not trade_no:
            raise ValueError("无效的回调数据")

        # 查找支付记录
        payment = await self.get_payment_by_transaction_id(db, trade_no)
        if not payment:
            raise ValueError("支付记录不存在")

        if payment.status == PaymentStatus.SUCCESS:
            return {"code": "success", "message": "已处理"}

        # 验证金额
        if float(total_amount) != payment.amount:
            raise ValueError("金额不匹配")

        # 更新支付状态
        if trade_status == "TRADE_SUCCESS":
            payment.status = PaymentStatus.SUCCESS
            payment.paid_at = datetime.utcnow()
            payment.transaction_id = trade_no
            payment.payment_data = str(callback_data)

            # 更新订单状态
            from app.services.order import order_service
            order = await order_service.get_order_by_id(db, payment.order_id)
            if order:
                order.status = "paid"
                order.paid_at = datetime.utcnow()

                # 自动发货
                await order_service.deliver_order(db, order)

        elif trade_status == "TRADE_CLOSED":
            payment.status = PaymentStatus.CANCELLED
        else:
            payment.status = PaymentStatus.FAILED

        await db.commit()

        return {"code": "success", "message": "处理成功"}

    async def handle_wechat_callback(self, db: AsyncSession, callback_data: dict) -> dict:
        """处理微信支付回调"""
        # 验证回调数据
        return_code = callback_data.get("return_code")
        result_code = callback_data.get("result_code")
        out_trade_no = callback_data.get("out_trade_no")
        transaction_id = callback_data.get("transaction_id")
        total_fee = callback_data.get("total_fee")

        if return_code != "SUCCESS":
            raise ValueError("回调失败")

        # 查找支付记录
        payment = await self.get_payment_by_transaction_id(db, transaction_id)
        if not payment:
            raise ValueError("支付记录不存在")

        if payment.status == PaymentStatus.SUCCESS:
            return {"code": "success", "message": "已处理"}

        # 验证金额（微信支付金额以分为单位）
        if int(total_fee) != int(payment.amount * 100):
            raise ValueError("金额不匹配")

        # 更新支付状态
        if result_code == "SUCCESS":
            payment.status = PaymentStatus.SUCCESS
            payment.paid_at = datetime.utcnow()
            payment.transaction_id = transaction_id
            payment.payment_data = str(callback_data)

            # 更新订单状态
            from app.services.order import order_service
            order = await order_service.get_order_by_id(db, payment.order_id)
            if order:
                order.status = "paid"
                order.paid_at = datetime.utcnow()

                # 自动发货
                await order_service.deliver_order(db, order)

        else:
            payment.status = PaymentStatus.FAILED

        await db.commit()

        return {"code": "success", "message": "处理成功"}

    async def delete_payment(self, db: AsyncSession, payment: Payment) -> None:
        """删除支付记录"""
        await db.delete(payment)
        await db.commit()


# 创建服务实例
payment_service = PaymentService()

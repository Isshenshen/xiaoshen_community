"""
卡密服务层
"""
from typing import List, Optional
from datetime import datetime
import secrets

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core.config import settings
from app.models.card import Card, CardStatus
from app.models.product import Product
from app.schemas.card import CardCreate, CardUpdate, CardBatchCreate


class CardService:
    """卡密服务"""

    def __init__(self):
        # 初始化加密器
        # Fernet需要32字节的base64编码密钥
        key_str = settings.CARD_ENCRYPTION_KEY

        # 检查密钥是否有效
        try:
            if len(key_str) < 32:
                raise ValueError("Key too short")

            key_bytes = key_str.encode()
            # 尝试创建Fernet对象来验证密钥
            Fernet(key_bytes)
            self.cipher = Fernet(key_bytes)
            print("[OK] Card encryption key validated successfully")
        except Exception as e:
            print("[INFO] Generating new encryption key...")
            # 确保生成44字符的base64编码密钥 (32字节base64编码的结果)
            new_key = secrets.token_urlsafe(32)
            # 如果长度不是44，重新生成直到符合要求
            while len(new_key) != 44:
                new_key = secrets.token_urlsafe(32)
            print(f"[KEY] New generated key: {new_key}")
            print("[TIP] Please copy this key to CARD_ENCRYPTION_KEY in .env file")

            self.cipher = Fernet(new_key.encode())

    def encrypt_content(self, content: str, secret: str) -> str:
        """加密卡密内容"""
        data = f"{secret}:{content}".encode()
        return self.cipher.encrypt(data).decode()

    def decrypt_content(self, encrypted_content: str) -> tuple[str, str]:
        """解密卡密内容"""
        try:
            data = self.cipher.decrypt(encrypted_content.encode()).decode()
            secret, content = data.split(':', 1)
            return secret, content
        except Exception:
            raise ValueError("卡密解密失败")

    async def get_cards(
        self,
        db: AsyncSession,
        product_id: Optional[int] = None,
        status: Optional[CardStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Card]:
        """获取卡密列表"""
        from sqlalchemy.orm import selectinload

        query = select(Card).options(selectinload(Card.product), selectinload(Card.user))

        conditions = []
        if product_id:
            conditions.append(Card.product_id == product_id)
        if status:
            conditions.append(Card.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(desc(Card.created_at))

        result = await db.execute(query)
        return result.scalars().all()

    async def get_card_by_id(self, db: AsyncSession, card_id: int) -> Optional[Card]:
        """根据ID获取卡密"""
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Card)
            .options(selectinload(Card.product), selectinload(Card.user))
            .where(Card.id == card_id)
        )
        return result.scalars().first()

    async def get_available_card(self, db: AsyncSession, product_id: int) -> Optional[Card]:
        """获取可用的卡密"""
        result = await db.execute(
            select(Card).where(
                and_(
                    Card.product_id == product_id,
                    Card.status == CardStatus.UNUSED,
                    or_(Card.expires_at.is_(None), Card.expires_at > datetime.utcnow())
                )
            ).limit(1)
        )
        return result.scalars().first()

    async def create_card(self, db: AsyncSession, card_in: CardCreate) -> Card:
        """创建卡密"""
        # 检查商品是否存在
        result = await db.execute(select(Product).where(Product.id == card_in.product_id))
        product = result.scalars().first()
        if not product:
            raise ValueError("商品不存在")

        # 生成解密密钥
        card_secret = secrets.token_hex(16)

        # 加密内容
        encrypted_content = self.encrypt_content(card_in.encrypted_content, card_secret)

        card = Card(
            product_id=card_in.product_id,
            encrypted_content=encrypted_content,
            card_secret=card_secret,
            expires_at=card_in.expires_at,
        )

        db.add(card)
        await db.commit()
        await db.refresh(card)
        return card

    async def batch_create_cards(
        self,
        db: AsyncSession,
        batch_in: CardBatchCreate
    ) -> List[Card]:
        """批量创建卡密"""
        # 检查商品是否存在
        result = await db.execute(select(Product).where(Product.id == batch_in.product_id))
        product = result.scalars().first()
        if not product:
            raise ValueError("商品不存在")

        cards = []
        for card_content in batch_in.card_contents:
            # 生成解密密钥
            card_secret = secrets.token_hex(16)

            # 加密内容
            encrypted_content = self.encrypt_content(card_content, card_secret)

            card = Card(
                product_id=batch_in.product_id,
                encrypted_content=encrypted_content,
                card_secret=card_secret,
                expires_at=batch_in.expires_at,
            )
            cards.append(card)

        db.add_all(cards)
        await db.commit()

        # 刷新所有卡密对象
        for card in cards:
            await db.refresh(card)

        return cards

    async def update_card(self, db: AsyncSession, card: Card, card_in: CardUpdate) -> Card:
        """更新卡密"""
        update_data = card_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(card, field, value)
        await db.commit()
        await db.refresh(card)
        return card

    async def use_card(self, db: AsyncSession, card: Card, user_id: int, order_id: Optional[int] = None) -> Card:
        """使用卡密"""
        if card.status != CardStatus.UNUSED:
            raise ValueError("卡密已被使用")

        if card.expires_at and card.expires_at < datetime.utcnow():
            # 标记为过期
            card.status = CardStatus.EXPIRED
            await db.commit()
            raise ValueError("卡密已过期")

        card.status = CardStatus.USED
        card.used_by = user_id
        card.used_at = datetime.utcnow()
        card.order_id = order_id

        await db.commit()
        await db.refresh(card)
        return card

    async def get_card_content(self, db: AsyncSession, card: Card) -> str:
        """获取卡密内容"""
        if card.status != CardStatus.USED:
            raise ValueError("卡密未被使用")

        try:
            secret, content = self.decrypt_content(card.encrypted_content)
            return content
        except Exception:
            raise ValueError("卡密内容获取失败")

    async def lock_card(self, db: AsyncSession, card: Card) -> Card:
        """锁定卡密"""
        card.status = CardStatus.LOCKED
        await db.commit()
        await db.refresh(card)
        return card

    async def unlock_card(self, db: AsyncSession, card: Card) -> Card:
        """解锁卡密"""
        if card.status == CardStatus.LOCKED:
            card.status = CardStatus.UNUSED
        await db.commit()
        await db.refresh(card)
        return card

    async def delete_card(self, db: AsyncSession, card: Card) -> None:
        """删除卡密"""
        await db.delete(card)
        await db.commit()


# 创建服务实例
card_service = CardService()

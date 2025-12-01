"""
Schema包初始化文件
"""
from .user import *
from .product import *
from .order import *
from .card import *
from .payment import *

__all__ = [
    # 用户相关
    "User", "UserCreate", "UserUpdate", "UserInDB", "Token", "TokenData", "LoginRequest",

    # 商品相关
    "Product", "ProductCreate", "ProductUpdate", "ProductList",
    "Category", "CategoryCreate", "CategoryUpdate",

    # 订单相关
    "Order", "OrderCreate", "OrderUpdate", "OrderList", "CartItem", "OrderSummary",

    # 卡密相关
    "Card", "CardCreate", "CardUpdate", "CardImport", "CardBatchCreate", "CardList",

    # 支付相关
    "Payment", "PaymentCreate", "PaymentUpdate", "PaymentList",
    "AlipayCallback", "WechatCallback",
]

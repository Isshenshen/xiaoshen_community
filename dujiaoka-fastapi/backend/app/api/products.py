"""
商品管理API

提供商品和分类的完整CRUD操作，包括：
- 商品分类管理（增删改查）
- 商品信息管理（增删改查）
- 商品搜索和筛选
- 库存管理
- 商品上下架控制

权限说明：
- 商品查询：公开访问
- 分类管理：仅管理员
- 商品管理：仅管理员
- 库存更新：仅管理员

数据关系：
- 商品属于分类（一对多）
- 商品可以有多个订单（一对多）
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_superuser, get_current_user
from app.models.user import User
from app.schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductList,
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate
)
from app.services.product import product_service

# 创建商品管理路由器
router = APIRouter(
    tags=["商品管理"]   # API文档分组标签
)


# ============================================================================
# 分类管理API
# ============================================================================

@router.get(
    "/categories",
    response_model=List[CategorySchema],
    summary="获取分类列表",
    description="""
    获取所有商品分类的列表。

    **分页参数：**
    - `skip`: 跳过的记录数（默认0）
    - `limit`: 返回的最大记录数（1-1000，默认100）

    **返回：** 分类列表，按排序权重排序
    """,
    responses={
        200: {"description": "获取成功"}
    }
)
async def read_categories(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的最大记录数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品分类列表

    返回所有启用的商品分类，支持分页查询。
    分类按sort_order字段排序。

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话

    Returns:
        List[CategorySchema]: 分类列表
    """
    categories = await product_service.get_categories(db, skip=skip, limit=limit)
    return categories


@router.post(
    "/categories",
    response_model=CategorySchema,
    summary="创建商品分类",
    description="""
    创建新的商品分类（仅管理员）。

    **输入参数：**
    - `name`: 分类名称（必填）
    - `description`: 分类描述（可选）
    - `sort_order`: 排序权重（可选，默认0）

    **权限：** 仅管理员可操作
    """,
    responses={
        200: {"description": "创建成功"},
        401: {"description": "未认证"},
        403: {"description": "权限不足"}
    }
)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    创建商品分类

    验证分类名称唯一性，创建新的商品分类。
    只有管理员可以执行此操作。

    Args:
        category_in: 分类创建数据
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        CategorySchema: 创建成功的分类信息

    Raises:
        HTTPException: 当分类名称重复时抛出400错误
    """
    try:
        category = await product_service.create_category(db, category_in)
        return category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """更新分类（管理员）"""
    category = await product_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    try:
        updated_category = await product_service.update_category(db, category, category_in)
        return updated_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """删除分类（管理员）"""
    category = await product_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )

    await product_service.delete_category(db, category)
    return {"message": "分类已删除"}


# ============================================================================
# 商品管理API
# ============================================================================

@router.get(
    "/",
    response_model=ProductList,
    summary="获取商品列表",
    description="""
    获取商品列表，支持分页、筛选和搜索。

    **查询参数：**
    - `skip`: 跳过的记录数（分页起始位置）
    - `limit`: 返回记录数（1-100）
    - `category_id`: 分类ID筛选
    - `search`: 商品名称搜索关键词

    **筛选条件：**
    - 只返回上架商品（is_active=true）
    - 按创建时间倒序排列

    **返回：** 分页的商品列表
    """,
    responses={
        200: {"description": "获取成功"}
    }
)
async def read_products(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    category_id: Optional[int] = Query(None, description="分类ID筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品列表

    支持多条件筛选和分页查询，返回上架商品列表。
    用于前端商品展示和搜索功能。

    Args:
        skip: 分页起始位置
        limit: 返回记录数
        category_id: 分类筛选（可选）
        search: 关键词搜索（可选）
        db: 数据库会话

    Returns:
        ProductList: 分页的商品列表
    """
    products = await product_service.get_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        is_active=True,  # 只显示上架商品
        search=search
    )

    # 获取总数（生产环境中应该用单独的count查询）
    # 这里简化处理，实际项目中需要优化
    total = len(products) if len(products) < limit else skip + limit + 1

    return ProductList(
        items=products,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get(
    "/{product_id}",
    response_model=ProductSchema,
    summary="获取商品详情",
    description="""
    根据商品ID获取单个商品的详细信息。

    **路径参数：**
    - `product_id`: 商品ID（必填）

    **返回：** 商品的完整信息，包括分类、价格、库存等

    **注意：** 只返回上架商品，未上架商品返回404
    """,
    responses={
        200: {"description": "获取成功"},
        404: {"description": "商品不存在或已下架"}
    }
)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品详情

    根据商品ID查询商品详细信息，只返回上架商品。
    用于商品详情页展示。

    Args:
        product_id: 商品ID
        db: 数据库会话

    Returns:
        ProductSchema: 商品详细信息

    Raises:
        HTTPException: 当商品不存在或未上架时抛出404错误
    """
    product = await product_service.get_product_by_id(db, product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
        )
    return product


@router.post(
    "/",
    response_model=ProductSchema,
    summary="创建商品",
    description="""
    创建新的商品信息（仅管理员）。

    **输入参数：**
    - `name`: 商品名称（必填）
    - `description`: 商品描述（可选）
    - `price`: 商品价格（必填）
    - `original_price`: 原价（可选）
    - `category_id`: 分类ID（可选）
    - `stock`: 库存数量（必填）
    - `auto_delivery`: 是否自动发货（可选）
    - `is_active`: 是否上架（可选）
    - `image_url`: 商品图片（可选）

    **权限：** 仅管理员可操作
    """,
    responses={
        200: {"description": "创建成功"},
        400: {"description": "数据验证错误"},
        401: {"description": "未认证"},
        403: {"description": "权限不足"}
    }
)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    创建商品

    验证商品数据有效性，创建新的商品记录。
    只有管理员可以执行此操作。

    Args:
        product_in: 商品创建数据
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        ProductSchema: 创建成功的商品信息

    Raises:
        HTTPException: 当数据验证失败时抛出400错误
    """
    try:
        product = await product_service.create_product(db, product_in)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{product_id}",
    response_model=ProductSchema,
    summary="更新商品信息",
    description="""
    更新现有商品的信息（仅管理员）。

    **路径参数：**
    - `product_id`: 商品ID（必填）

    **可更新字段：**
    - `name`: 商品名称
    - `description`: 商品描述
    - `price`: 商品价格
    - `stock`: 库存数量
    - `is_active`: 上架状态
    - `image_url`: 商品图片
    - 等等...

    **权限：** 仅管理员可操作
    """,
    responses={
        200: {"description": "更新成功"},
        400: {"description": "数据验证错误"},
        404: {"description": "商品不存在"}
    }
)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    更新商品信息

    根据商品ID查找并更新商品，支持部分更新。
    验证数据的有效性，处理外键关联等。

    Args:
        product_id: 商品ID
        product_in: 商品更新数据
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        ProductSchema: 更新后的商品信息

    Raises:
        HTTPException: 当商品不存在或数据无效时抛出相应错误
    """
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    try:
        updated_product = await product_service.update_product(db, product, product_in)
        return updated_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{product_id}",
    summary="删除商品",
    description="""
    删除指定的商品（仅管理员）。

    **路径参数：**
    - `product_id`: 要删除的商品ID

    **注意：** 此操作会将商品标记为删除状态，
    而不是物理删除，以保持数据完整性。

    **权限：** 仅管理员可操作
    """,
    responses={
        200: {"description": "删除成功"},
        404: {"description": "商品不存在"}
    }
)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    删除商品

    将商品标记为删除状态（软删除），而不是物理删除。
    检查是否有未完成的订单等依赖关系。

    Args:
        product_id: 商品ID
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        dict: 操作成功消息

    Raises:
        HTTPException: 当商品不存在时抛出404错误
    """
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    await product_service.delete_product(db, product)
    return {"message": "商品已下架"}


@router.post(
    "/{product_id}/stock",
    summary="更新商品库存",
    description="""
    更新指定商品的库存数量（仅管理员）。

    **路径参数：**
    - `product_id`: 商品ID

    **请求体参数：**
    - `quantity`: 新的库存数量

    **注意：**
    - 库存数量可以设置为0（缺货）
    - 可以设置为-1表示无限库存
    - 库存变化会影响商品的购买状态

    **权限：** 仅管理员可操作
    """,
    responses={
        200: {"description": "库存更新成功"},
        400: {"description": "库存数量无效"},
        404: {"description": "商品不存在"}
    }
)
async def update_product_stock(
    product_id: int,
    quantity: int,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    更新商品库存

    修改商品的库存数量，用于库存管理和补货操作。
    支持设置无限库存（-1）和其他特殊值。

    Args:
        product_id: 商品ID
        quantity: 新的库存数量
        current_user: 当前管理员用户
        db: 数据库会话

    Returns:
        dict: 包含成功消息和更新后的库存数量

    Raises:
        HTTPException: 当商品不存在或库存无效时抛出相应错误
    """
    product = await product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    try:
        updated_product = await product_service.update_stock(db, product, quantity)
        return {
            "message": "库存更新成功",
            "stock": updated_product.stock
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

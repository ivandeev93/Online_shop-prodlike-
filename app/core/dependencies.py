from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

from app.repositories.cart import CartRepository
from app.repositories.category import CategoryRepository
from app.repositories.order import OrderRepository
from app.repositories.product import ProductRepository
from app.repositories.review import ReviewRepository
from app.repositories.user import UserRepository

from app.services.cart import CartService
from app.services.category import CategoryService
from app.services.order import OrderService
from app.services.product import ProductService
from app.services.review import ReviewService
from app.services.user import UserService


# Зависимость базы данных
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


# Зависимости репозиториев
def get_cart_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CartRepository:
    return CartRepository(db=db)


def get_category_repository(
    db: AsyncSession = Depends(get_async_db),
) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_order_repository(
    db: AsyncSession = Depends(get_async_db),
) -> OrderRepository:
    return OrderRepository(db=db)


def get_product_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ProductRepository:
    return ProductRepository(db=db)


def get_review_repository(
    db: AsyncSession = Depends(get_async_db),
) -> ReviewRepository:
    return ReviewRepository(db=db)


def get_user_repository(
    db: AsyncSession = Depends(get_async_db),
) -> UserRepository:
    return UserRepository(db=db)


# Зависимости сервисов
def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    db: AsyncSession = Depends(get_async_db),
) -> CartService:
    return CartService(
        cart_repo=cart_repo,
        product_repo=product_repo,
        db=db,
    )


def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository),
    db: AsyncSession = Depends(get_async_db),
) -> CategoryService:
    return CategoryService(
        category_repo=category_repo,
        db=db,
    )


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    db: AsyncSession = Depends(get_async_db),
) -> OrderService:
    return OrderService(
        order_repo=order_repo,
        cart_repo=cart_repo,
        product_repo=product_repo,
        db=db,
    )


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
    db: AsyncSession = Depends(get_async_db),
) -> ProductService:
    return ProductService(
        product_repo=product_repo,
        category_repo=category_repo,
        db=db,
    )


def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    db: AsyncSession = Depends(get_async_db),
) -> ReviewService:
    return ReviewService(
        review_repo=review_repo,
        product_repo=product_repo,
        db=db,
    )


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_async_db),
) -> UserService:
    return UserService(
        user_repo=user_repo,
        db=db,
    )

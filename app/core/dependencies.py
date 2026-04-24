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



async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


# Зависимости для получения экземпляров репозиториев
# Сущности у которых есть внешний ключ проверяют существование связанных
def get_cart_repository(db: AsyncSession = Depends(get_async_db)) -> CartRepository:
    return CartRepository(db=db)


def get_category_repository(db: AsyncSession = Depends(get_async_db)) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_order_repository(db: AsyncSession = Depends(get_async_db)) -> OrderRepository:
    return OrderRepository(db=db)


def get_product_repository(db: AsyncSession = Depends(get_async_db)) -> ProductRepository:
    return ProductRepository(db=db)


def get_review_repository(db: AsyncSession = Depends(get_async_db)) -> ReviewRepository:
    return ReviewRepository(db=db)


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db=db)


# Зависимости для получения экземпляров сервисов
def get_cart_service(repo: CartRepository = Depends(get_cart_repository)) -> CartService:
    return CartService(cart_repo=repo)


def get_category_service(repo: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repo=repo)


def get_order_service(repo: OrderRepository = Depends(get_order_repository)) -> OrderService:
    return OrderService(order_repo=repo)


def get_product_service(repo: ProductRepository = Depends(get_product_repository)) -> ProductService:
    return ProductService(product_repo=repo)


def get_review_repository(repo: ReviewRepository = Depends(get_review_repository)) -> ReviewService:
    return ReviewService(review_repo=repo)


def get_user_repository(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo=repo)
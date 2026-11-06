from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import cart, categories, orders, products, reviews, users
from app.core.database import close_database_connection

from app.core.exception_handlers import (
    category_not_found_handler,
    category_already_exists_handler,
    product_not_found_handler,
    product_permission_denied_handler,
    user_already_exists_handler,
    user_not_found_handler,
    unauthorized_user_handler,
    cart_item_not_found_handler,
    insufficient_stock_handler,
    cart_is_empty_handler,
    order_not_found_handler,
    order_product_unavailable_handler,
    review_not_found_handler,
    review_already_exists_handler,
    review_permission_denied_handler,
)

from app.exceptions.category import (
    CategoryNotFoundError,
    CategoryAlreadyExistsError,
)
from app.exceptions.product import (
    ProductNotFoundError,
    ProductPermissionDeniedError,
)
from app.exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UnauthorizedUserError,
)
from app.exceptions.cart import (
    CartItemNotFoundError,
    InsufficientStockError,
)
from app.exceptions.order import (
    CartIsEmptyError,
    OrderNotFoundError,
    OrderProductUnavailableError,
)
from app.exceptions.review import (
    ReviewNotFoundError,
    ReviewAlreadyExistsError,
    ReviewPermissionDeniedError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается.")

    try:
        yield
    finally:
        await close_database_connection()
        print("Приложение завершает работу.")


app = FastAPI(
    title="Online Shop API",
    lifespan=lifespan,
)


# Подключение маршрутов
app.include_router(cart.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)


# Обработчики ошибок категорий
app.add_exception_handler(
    CategoryNotFoundError,
    category_not_found_handler,
)

app.add_exception_handler(
    CategoryAlreadyExistsError,
    category_already_exists_handler,
)


# Обработчики ошибок товаров
app.add_exception_handler(
    ProductNotFoundError,
    product_not_found_handler,
)

app.add_exception_handler(
    ProductPermissionDeniedError,
    product_permission_denied_handler,
)


# Обработчики ошибок пользователей
app.add_exception_handler(
    UserAlreadyExistsError,
    user_already_exists_handler,
)

app.add_exception_handler(
    UserNotFoundError,
    user_not_found_handler,
)

app.add_exception_handler(
    UnauthorizedUserError,
    unauthorized_user_handler,
)

# Обработчики ошибок корзины
app.add_exception_handler(
    CartItemNotFoundError,
    cart_item_not_found_handler,
)

app.add_exception_handler(
    InsufficientStockError,
    insufficient_stock_handler,
)

app.add_exception_handler(
    CartIsEmptyError,
    cart_is_empty_handler,
)

# Обработчики ошибок заказов
app.add_exception_handler(
    OrderNotFoundError,
    order_not_found_handler,
)
app.add_exception_handler(
    OrderProductUnavailableError,
    order_product_unavailable_handler,
)

# Обработчики ошибок отзывов
app.add_exception_handler(
    ReviewNotFoundError,
    review_not_found_handler,
)

app.add_exception_handler(
    ReviewAlreadyExistsError,
    review_already_exists_handler,
)

app.add_exception_handler(
    ReviewPermissionDeniedError,
    review_permission_denied_handler,
)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Online Shop API"}

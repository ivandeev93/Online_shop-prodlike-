from fastapi import Request, status
from fastapi.responses import JSONResponse

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


async def category_not_found_handler(
    request: Request,
    exc: CategoryNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда категория не найдена."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def category_already_exists_handler(
    request: Request,
    exc: CategoryAlreadyExistsError,
) -> JSONResponse:
    """Обрабатывает попытку создать уже существующую категорию."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def product_not_found_handler(
    request: Request,
    exc: ProductNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда товар не найден."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def product_permission_denied_handler(
    request: Request,
    exc: ProductPermissionDeniedError,
) -> JSONResponse:
    """Обрабатывает отсутствие прав на управление товаром."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsError,
) -> JSONResponse:
    """Обрабатывает попытку регистрации с уже существующим email."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда пользователь не найден."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def unauthorized_user_handler(
    request: Request,
    exc: UnauthorizedUserError,
) -> JSONResponse:
    """Обрабатывает ошибки аутентификации пользователя."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def cart_item_not_found_handler(
    request: Request,
    exc: CartItemNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда позиция корзины не найдена."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def insufficient_stock_handler(
    request: Request,
    exc: InsufficientStockError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда запрошено больше товара, чем есть на складе."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def cart_is_empty_handler(
    request: Request,
    exc: CartIsEmptyError,
) -> JSONResponse:
    """Обрабатывает попытку оформления заказа с пустой корзиной."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def order_not_found_handler(
    request: Request,
    exc: OrderNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда заказ не найден."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def order_product_unavailable_handler(
    request: Request,
    exc: OrderProductUnavailableError,
) -> JSONResponse:
    """Обрабатывает попытку купить недоступный товар."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def review_not_found_handler(
    request: Request,
    exc: ReviewNotFoundError,
) -> JSONResponse:
    """Обрабатывает ситуацию, когда отзыв не найден."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def review_already_exists_handler(
    request: Request,
    exc: ReviewAlreadyExistsError,
) -> JSONResponse:
    """Обрабатывает попытку повторно оставить отзыв."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def review_permission_denied_handler(
    request: Request,
    exc: ReviewPermissionDeniedError,
) -> JSONResponse:
    """Обрабатывает отсутствие прав на выполнение операции с отзывом."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )

from fastapi import APIRouter, Depends, Response, status

from app.auth import get_current_user
from app.core.dependencies import get_cart_service
from app.models.users import User
from app.schemas import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartItemUpdate,
)
from app.services.cart import CartService


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartSchema)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Возвращает корзину текущего пользователя.
    """
    return await cart_service.get_cart(current_user.id)


@router.post(
    "/items", response_model=CartItemSchema, status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    payload: CartItemCreate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Добавляет товар в корзину текущего пользователя.
    """
    return await cart_service.add_item(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )


@router.put("/items/{product_id}", response_model=CartItemSchema)
async def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Обновляет количество товара в корзине.
    """
    return await cart_service.update_item(
        user_id=current_user.id,
        product_id=product_id,
        quantity=payload.quantity,
    )


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Удаляет товар из корзины.
    """
    await cart_service.remove_item(
        user_id=current_user.id,
        product_id=product_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    """
    Полностью очищает корзину текущего пользователя.
    """
    await cart_service.clear_cart(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

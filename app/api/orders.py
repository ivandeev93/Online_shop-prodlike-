from fastapi import APIRouter, Depends, Query, status

from app.auth import get_current_user
from app.core.dependencies import get_order_service
from app.models.users import User
from app.schemas import Order as OrderSchema, OrderList
from app.services.order import OrderService


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/checkout",
    response_model=OrderSchema,
    status_code=status.HTTP_201_CREATED,
)
async def checkout_order(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Оформляет заказ на основе корзины текущего пользователя.
    """
    return await order_service.checkout(user_id=current_user.id)


@router.get("/", response_model=OrderList)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Возвращает заказы текущего пользователя с пагинацией.
    """
    return await order_service.get_user_orders(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Возвращает подробную информацию о заказе.
    """
    return await order_service.get_order(
        order_id=order_id,
        user_id=current_user.id,
    )

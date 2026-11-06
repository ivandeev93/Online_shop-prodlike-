from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.orders import Order, OrderItem


class OrderRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        total_amount: Decimal,
        items: list[dict],
    ) -> Order:
        """Создаёт заказ вместе с его позициями."""
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            items=[
                OrderItem(**item)
                for item in items
            ],
        )

        self.db.add(order)
        await self.db.flush()

        return order

    async def get_by_id(
        self,
        order_id: int,
        user_id: int,
    ) -> Order | None:
        """Получает заказ пользователя вместе с позициями и товарами."""
        result = await self.db.scalar(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
            .where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )

        return result

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[Sequence[Order], int]:
        """Получает заказы пользователя с пагинацией."""
        total = await self.db.scalar(
            select(func.count(Order.id))
            .where(Order.user_id == user_id)
        )

        result = await self.db.scalars(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.all(), total or 0

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.cart_items import CartItem


class CartItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by(self, cart: str) -> CartItem | None:
        result = await self.db.scalar(select())
        return result


# app/repositories/cart_repository.py

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_items import CartItem as CartItemModel
from app.models.products import Product as ProductModel


class CartRepository:

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int):
        result = await db.scalars(
            select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True,
            )
        )
        return result.first()

    @staticmethod
    async def get_cart_item(db: AsyncSession, user_id: int, product_id: int):
        result = await db.scalars(
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(
                CartItemModel.user_id == user_id,
                CartItemModel.product_id == product_id,
            )
        )
        return result.first()

    @staticmethod
    async def get_cart_items(db: AsyncSession, user_id: int):
        result = await db.scalars(
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.id)
        )
        return result.all()

    @staticmethod
    async def add(db: AsyncSession, cart_item: CartItemModel):
        db.add(cart_item)

    @staticmethod
    async def delete(db: AsyncSession, cart_item: CartItemModel):
        await db.delete(cart_item)

    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: int):
        await db.execute(
            delete(CartItemModel).where(CartItemModel.user_id == user_id)
        )
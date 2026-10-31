from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_items import CartItem as CartItemModel
from app.models.products import Product as ProductModel


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product(self, product_id: int):
        result = await self.db.scalars(
            select(ProductModel).where(
                ProductModel.id == product_id,
                ProductModel.is_active == True,
            )
        )
        return result.first()

    async def get_cart_item(self, user_id: int, product_id: int) -> CartItemModel | None:
        result = await self.db.scalars(
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(
                CartItemModel.user_id == user_id,
                CartItemModel.product_id == product_id,
            )
        )
        return result.first()

    async def get_cart_items(self, user_id: int):
        result = await self.db.scalars(
            select(CartItemModel)
            .options(selectinload(CartItemModel.product))
            .where(CartItemModel.user_id == user_id)
            .order_by(CartItemModel.id)
        )
        return result.all()

    async def add(self, cart_item: CartItemModel):
        self.db.add(cart_item)

    async def delete(self, cart_item: CartItemModel):
        await self.db.delete(cart_item)

    async def clear_cart(self, user_id: int):
        await self.db.execute(
            delete(CartItemModel).where(CartItemModel.user_id == user_id)
        )
# CartService

from decimal import Decimal
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.core.dependencies import get_async_db

from app.models.users import User as UserModel
from app.models.cart_items import CartItem as CartItemModel
from app.repositories.cart import CartRepository
from app.schemas import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartItemUpdate
)

class CartService:
    def __init__(self, cart_repo: CartRepository):
        self.

    @staticmethod
    async def _ensure_product_available(db: AsyncSession, product_id: int) -> None:
        product = await CartRepository.get_product(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive",
            )

    @staticmethod
    async def get_cart(db: AsyncSession, current_user: UserModel = Depends(get_current_user)):
        items = await CartRepository.get_cart_items(db, current_user.id)

        total_quantity = sum(item.quantity for item in items)

        total_price = sum(
            Decimal(item.quantity) *
            (item.product.price or Decimal("0"))
            for item in items
        )

        return CartSchema(
            user_id=current_user.id,
            items=items,
            total_quantity=total_quantity,
            total_price=total_price,
        )

    @staticmethod
    async def add_item(db: AsyncSession, user_id: int, product_id: int, quantity: int):
        await CartService._ensure_product_available(db, product_id)

        cart_item = await CartRepository.get_cart_item(db, user_id, product_id)

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItemModel(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
            )
            await CartRepository.add(db, cart_item)

        await db.commit()

        return await CartRepository.get_cart_item(db, user_id, product_id)

    @staticmethod
    async def update_item(db: AsyncSession, user_id: int, product_id: int, quantity: int):
        await CartService._ensure_product_available(db, product_id)

        cart_item = await CartRepository.get_cart_item(db, user_id, product_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        cart_item.quantity = quantity
        await db.commit()

        return await CartRepository.get_cart_item(db, user_id, product_id)

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: int, product_id: int):
        cart_item = await CartRepository.get_cart_item(db, user_id, product_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        await CartRepository.delete(db, cart_item)
        await db.commit()

    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: int):
        await CartRepository.clear_cart(db, user_id)
        await db.commit()
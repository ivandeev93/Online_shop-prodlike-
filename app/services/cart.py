from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.cart import (
    CartItemNotFoundError,
    InsufficientStockError,
    InvalidCartQuantityError,
)
from app.exceptions.product import ProductNotFoundError
from app.models.cart_items import CartItem
from app.repositories.cart import CartRepository
from app.repositories.product import ProductRepository
from app.schemas import Cart as CartSchema


class CartService:

    def __init__(
        self,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        db: AsyncSession,
    ):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.db = db

    async def get_cart(self, user_id: int) -> CartSchema:
        """
        Получает корзину пользователя и рассчитывает её стоимость.
        """
        items = await self.cart_repo.get_by_user_id(user_id)

        total_quantity = sum(item.quantity for item in items)

        total_price = sum(
            (
                item.product.price * item.quantity
                for item in items
            ),
            start=Decimal("0.00"),
        )

        return CartSchema(
            user_id=user_id,
            items=items,
            total_quantity=total_quantity,
            total_price=total_price,
        )

    async def add_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:
        """
        Добавляет товар в корзину или увеличивает его количество.
        """
        if quantity < 1:
            raise InvalidCartQuantityError()

        try:
            # Блокируем пользователя, чтобы сериализовать операции с его корзиной.
            await self.cart_repo.lock_user_cart(user_id)

            # Блокируем существующую позицию корзины.
            existing_item = (
                await self.cart_repo.get_by_product_id_for_update(
                    user_id=user_id,
                    product_id=product_id,
                )
            )

            # Блокируем товар для проверки актуального остатка.
            product = await self.product_repo.get_by_id_for_update(
                product_id
            )

            if product is None or not product.is_active:
                raise ProductNotFoundError()

            current_quantity = (
                existing_item.quantity
                if existing_item is not None
                else 0
            )

            new_quantity = current_quantity + quantity

            if new_quantity > product.stock:
                raise InsufficientStockError(
                    "Requested quantity exceeds available stock"
                )

            if existing_item is not None:
                await self.cart_repo.update_quantity(
                    cart_item=existing_item,
                    quantity=new_quantity,
                )
            else:
                await self.cart_repo.create(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                )

            # Получаем позицию вместе с товаром до фиксации транзакции.
            cart_item = await self.cart_repo.get_by_product_id(
                user_id=user_id,
                product_id=product_id,
            )

            if cart_item is None:
                raise CartItemNotFoundError()

            await self.db.commit()

            return cart_item

        except Exception:
            await self.db.rollback()
            raise

    async def update_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:
        """
        Устанавливает новое количество товара в корзине.
        """
        if quantity < 1:
            raise InvalidCartQuantityError()

        try:
            # Блокируем пользователя перед изменением корзины.
            await self.cart_repo.lock_user_cart(user_id)

            # Получаем и блокируем позицию корзины.
            cart_item = (
                await self.cart_repo.get_by_product_id_for_update(
                    user_id=user_id,
                    product_id=product_id,
                )
            )

            if cart_item is None:
                raise CartItemNotFoundError()

            # Блокируем товар для проверки актуального остатка.
            product = await self.product_repo.get_by_id_for_update(
                product_id
            )

            if product is None or not product.is_active:
                raise ProductNotFoundError()

            if quantity > product.stock:
                raise InsufficientStockError(
                    "Requested quantity exceeds available stock"
                )

            await self.cart_repo.update_quantity(
                cart_item=cart_item,
                quantity=quantity,
            )

            # Получаем обновлённую позицию вместе с товаром.
            updated_item = await self.cart_repo.get_by_product_id(
                user_id=user_id,
                product_id=product_id,
            )

            if updated_item is None:
                raise CartItemNotFoundError()

            await self.db.commit()

            return updated_item

        except Exception:
            await self.db.rollback()
            raise

    async def remove_item(
        self,
        user_id: int,
        product_id: int,
    ) -> None:
        """
        Удаляет товар из корзины пользователя.
        """
        try:
            # Блокируем пользователя перед изменением корзины.
            await self.cart_repo.lock_user_cart(user_id)

            # Получаем и блокируем позицию корзины.
            cart_item = (
                await self.cart_repo.get_by_product_id_for_update(
                    user_id=user_id,
                    product_id=product_id,
                )
            )

            if cart_item is None:
                raise CartItemNotFoundError()

            await self.cart_repo.delete(cart_item)
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

    async def clear_cart(self, user_id: int) -> None:
        """
        Удаляет все позиции из корзины пользователя.
        """
        try:
            # Блокируем пользователя перед очисткой корзины.
            await self.cart_repo.lock_user_cart(user_id)

            await self.cart_repo.clear(user_id)
            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

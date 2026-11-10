from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_items import CartItem
from app.models.users import User

class CartRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> list[CartItem]:
        """
        Получает все позиции корзины пользователя.
        """
        result = await self.db.scalars(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        )

        return list(result.all())

    async def get_by_id(self, item_id: int, user_id: int) -> CartItem | None:
        """
        Получает позицию корзины по ID с проверкой владельца.
        """
        result = await self.db.scalar(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(
                CartItem.id == item_id,
                CartItem.user_id == user_id,
            )
        )

        return result

    async def get_by_product_id(
        self, user_id: int, product_id: int,
    ) -> CartItem | None:
        """
        Находит позицию корзины по ID пользователя и товара.
        """
        result = await self.db.scalar(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )

        return result

    async def get_by_product_id_for_update(
        self, user_id: int, product_id: int,
    ) -> CartItem | None:
        """
        Получает позицию корзины и блокирует её до завершения транзакции.
        """
        result = await self.db.scalar(
            select(CartItem)
            .where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
            .with_for_update()
        )

        return result

    async def create(
        self, user_id: int, product_id: int, quantity: int,
    ) -> CartItem:
        """
        Добавляет новую позицию в корзину.
        """
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )

        self.db.add(cart_item)
        await self.db.flush()

        return cart_item

    async def update_quantity(
        self, cart_item: CartItem, quantity: int,
    ) -> CartItem:
        """
        Обновляет количество товара в корзине.
        """
        cart_item.quantity = quantity
        await self.db.flush()

        return cart_item

    async def delete(self, cart_item: CartItem) -> None:
        """
        Удаляет отдельную позицию из корзины.
        """
        await self.db.delete(cart_item)
        await self.db.flush()

    async def clear(self, user_id: int) -> None:
        """
        Удаляет все позиции корзины пользователя.
        """
        await self.db.execute(
            delete(CartItem).where(CartItem.user_id == user_id)
        )
        await self.db.flush()

    async def get_by_user_id_for_update(self, user_id: int) -> list[CartItem]:
        """
        Получает позиции корзины и блокирует их до завершения транзакции.
        """
        result = await self.db.scalars(
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
            .with_for_update()
        )

        return list(result.all())

    async def lock_user_cart(self, user_id: int) -> None:
        """
        Блокирует строку пользователя на время изменения его корзины.
        """
        await self.db.scalar(
            select(User)
            .where(User.id == user_id)
            .with_for_update()
        )

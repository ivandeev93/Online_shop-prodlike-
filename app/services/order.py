from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.cart import InsufficientStockError
from app.exceptions.order import (
    CartIsEmptyError,
    OrderNotFoundError,
    OrderProductUnavailableError,
)
from app.models.orders import Order
from app.models.cart_items import CartItem
from app.repositories.cart import CartRepository
from app.repositories.order import OrderRepository
from app.repositories.product import ProductRepository
from app.schemas import OrderList


class OrderService:

    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        db: AsyncSession,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.db = db

    async def checkout(self, user_id: int) -> Order:
        """Оформляет заказ на основе корзины пользователя."""
        try:
            # Блокируем позиции корзины, чтобы исключить повторное оформление.
            cart_items = await self.cart_repo.get_by_user_id_for_update(
                user_id
            )

            if not cart_items:
                raise CartIsEmptyError()

            # Блокируем товары в едином порядке по ID.
            product_ids: list[int] = sorted({
                item.product_id
                for item in cart_items
            })

            products = await self.product_repo.get_by_ids_for_update(
                product_ids
            )

            products_by_id = {
                product.id: product
                for product in products
            }

            order_items = []
            total_amount = Decimal("0.00")

            # Проверяем товары и формируем позиции заказа.
            for cart_item in cart_items:
                product = products_by_id.get(cart_item.product_id)

                if product is None or not product.is_active:
                    raise OrderProductUnavailableError(
                        f"Product {cart_item.product_id} is unavailable"
                    )

                if product.stock < cart_item.quantity:
                    raise InsufficientStockError(
                        f"Not enough stock for product '{product.name}'"
                    )

                unit_price = product.price
                item_total = unit_price * cart_item.quantity

                order_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "quantity": cart_item.quantity,
                    "unit_price": unit_price,
                })

                total_amount += item_total

            # Уменьшаем остатки только после проверки всех позиций.
            for cart_item in cart_items:
                product = products_by_id[cart_item.product_id]
                product.stock -= cart_item.quantity

            # Создаём заказ и сохраняем снимки названий и цен.
            order = await self.order_repo.create(
                user_id=user_id,
                total_amount=total_amount,
                items=order_items,
            )

            # Очищаем корзину в рамках той же транзакции.
            await self.cart_repo.clear(user_id)

            await self.db.commit()

            # Повторно получаем заказ вместе с товарами для ответа API.
            created_order = await self.order_repo.get_by_id(
                order_id=order.id,
                user_id=user_id,
            )

            if created_order is None:
                raise OrderNotFoundError(
                    "Created order could not be loaded"
                )

            return created_order

        except Exception:
            await self.db.rollback()
            raise

    async def get_user_orders(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> OrderList:
        """Получает список заказов пользователя с пагинацией."""
        skip = (page - 1) * page_size

        orders, total = await self.order_repo.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=page_size,
        )

        return OrderList(
            items=orders,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        """Получает заказ пользователя по его ID."""
        order = await self.order_repo.get_by_id(
            order_id=order_id,
            user_id=user_id,
        )

        if order is None:
            raise OrderNotFoundError()

        return order

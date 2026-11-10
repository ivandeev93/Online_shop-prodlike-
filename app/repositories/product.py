from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product
from app.models.categories import Category


class ProductRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: int | None = None,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
        seller_id: int | None = None,
    ) -> tuple[Sequence[Product], int]:

        filters = [
            Product.is_active.is_(True),
            Category.is_active.is_(True),
        ]

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        if min_price is not None:
            filters.append(Product.price >= min_price)

        if max_price is not None:
            filters.append(Product.price <= max_price)

        if in_stock is not None:
            if in_stock:
                filters.append(Product.stock > 0)
            else:
                filters.append(Product.stock == 0)

        if seller_id is not None:
            filters.append(Product.seller_id == seller_id)

        search_value = search.strip() if search else None
        rank_column = None

        if search_value:
            ts_query = func.websearch_to_tsquery("english", search_value)
            filters.append(Product.tsv.op("@@")(ts_query))
            rank_column = func.ts_rank_cd(
                Product.tsv,
                ts_query
            )

        total_stmt = (
            select(func.count(Product.id))
            .select_from(Product)
            .join(Product.category)
            .where(*filters)
        )

        total = await self.db.scalar(total_stmt) or 0

        products_stmt = (
            select(Product)
            .join(Product.category)
            .where(*filters)
        )

        if rank_column is not None:
            products_stmt = products_stmt.order_by(
                desc(rank_column),
                Product.id
            )
        else:
            products_stmt = products_stmt.order_by(Product.id)

        products_stmt = (
            products_stmt
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.scalars(products_stmt)

        return result.all(), total

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.db.scalar(
            select(Product)
            .where(
                Product.id == product_id,
                Product.is_active.is_(True),
            )
        )

    async def get_by_seller(
        self,
        seller_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Product]:
        result = await self.db.scalars(
            select(Product)
            .where(
                Product.seller_id == seller_id,
                Product.is_active.is_(True),
            )
            .order_by(Product.id)
            .offset(skip)
            .limit(limit)
        )

        return result.all()

    async def create(
        self,
        name: str,
        description: str | None,
        price: Decimal,
        image_url: str | None,
        stock: int,
        category_id: int,
        seller_id: int,
    ) -> Product:
        """
        Создаёт товар.
        """
        db_product = Product(
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            stock=stock,
            category_id=category_id,
            seller_id=seller_id,
        )

        self.db.add(db_product)
        await self.db.flush()

        return db_product

    async def update(
        self,
        product_id: int,
        values: dict[str, Any],
    ) -> Product | None:
        """
        Обновляет товар.
        """
        db_product = await self.get_by_id(product_id)

        if db_product is None:
            return None

        allowed_fields = {
            "name",
            "description",
            "price",
            "image_url",
            "stock",
            "category_id",
        }

        for field, value in values.items():
            if field not in allowed_fields:
                raise ValueError(
                    f"Field '{field}' cannot be updated"
                )

            setattr(db_product, field, value)

        await self.db.flush()

        return db_product

    async def update_rating(
            self,
            product_id: int,
            rating: Decimal,
    ) -> Product | None:
        """
        Обновляет средний рейтинг товара.
        """
        db_product = await self.db.get(Product, product_id)

        if db_product is None:
            return None

        db_product.rating = rating

        await self.db.flush()

        return db_product

    async def delete(self, product_id: int) -> Product | None:
        db_product = await self.get_by_id(product_id)

        if db_product is None:
            return None

        db_product.is_active = False

        await self.db.flush()

        return db_product

    async def get_by_ids_for_update(
        self,
        product_ids: list[int],
    ) -> list[Product]:
        """
        Получает товары и блокирует их до завершения транзакции.
        """
        if not product_ids:
            return []

        result = await self.db.scalars(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
        )

        return list(result.all())

    async def get_by_id_for_update(self, product_id: int) -> Product | None:
        """
        Получает товар и блокирует его до завершения транзакции.
        """
        return await self.db.scalar(
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()
        )
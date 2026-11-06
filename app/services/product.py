from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.category import CategoryNotFoundError
from app.exceptions.product import (
    ProductNotFoundError,
    ProductPermissionDeniedError,
)
from app.models.products import Product
from app.models.users import User
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        db: AsyncSession,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.db = db

    @staticmethod
    def _check_product_permission(
        product: Product,
        current_user: User,
    ) -> None:
        """
        Проверяет право пользователя управлять товаром.
        """
        if current_user.role == "admin":
            return

        if (
            current_user.role != "seller"
            or product.seller_id != current_user.id
        ):
            raise ProductPermissionDeniedError()

    async def get_all_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: int | None = None,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
        seller_id: int | None = None,
    ) -> tuple[Sequence[Product], int]:

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError(
                    "min_price cannot be greater than max_price"
                )

        skip = (page - 1) * page_size

        return await self.product_repo.get_all(
            skip=skip,
            limit=page_size,
            category_id=category_id,
            search=search,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            seller_id=seller_id,
        )

    async def get_product_by_id(self, product_id: int) -> Product:
        product = await self.product_repo.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundError()

        category = await self.category_repo.get_by_id(product.category_id)

        if category is None:
            raise ProductNotFoundError()

        return product

    async def get_products_by_seller(
        self,
        seller_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Product]:

        return await self.product_repo.get_by_seller(
            seller_id=seller_id,
            skip=skip,
            limit=limit,
        )

    async def create_product(
        self,
        product: ProductCreate,
        current_user: User,
        image_url: str | None = None,
    ) -> Product:

        if current_user.role != "seller":
            raise ProductPermissionDeniedError(
                "Only sellers can create products"
            )

        category = await self.category_repo.get_by_id(product.category_id)

        if category is None:
            raise CategoryNotFoundError()

        try:
            db_product = await self.product_repo.create(
                name=product.name,
                description=product.description,
                price=product.price,
                image_url=image_url,
                stock=product.stock,
                category_id=product.category_id,
                seller_id=current_user.id,
            )

            await self.db.commit()
            await self.db.refresh(db_product)

            return db_product

        except Exception:
            await self.db.rollback()
            raise

    async def update_product(
        self,
        product_id: int,
        product: ProductUpdate,
        current_user: User,
        image_url: str | None = None,
    ) -> tuple[Product, str | None]:

        db_product = await self.product_repo.get_by_id(product_id)

        if db_product is None:
            raise ProductNotFoundError()

        self._check_product_permission(db_product, current_user)

        values = product.model_dump(exclude_unset=True)

        if "category_id" in values:
            category = await self.category_repo.get_by_id(
                values["category_id"]
            )

            if category is None:
                raise CategoryNotFoundError()

        old_image_url = db_product.image_url if image_url is not None else None

        if image_url is not None:
            values["image_url"] = image_url

        try:
            updated_product = await self.product_repo.update(
                product_id=product_id,
                values=values,
            )

            if updated_product is None:
                raise ProductNotFoundError()

            await self.db.commit()
            await self.db.refresh(updated_product)

            return updated_product, old_image_url

        except Exception:
            await self.db.rollback()
            raise

    async def delete_product(
        self,
        product_id: int,
        current_user: User,
    ) -> Product:

        db_product = await self.product_repo.get_by_id(product_id)

        if db_product is None:
            raise ProductNotFoundError()

        self._check_product_permission(db_product, current_user)

        try:
            deleted_product = await self.product_repo.delete(product_id)

            if deleted_product is None:
                raise ProductNotFoundError()

            await self.db.commit()
            await self.db.refresh(deleted_product)

            return deleted_product

        except Exception:
            await self.db.rollback()
            raise

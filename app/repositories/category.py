from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Category]:
        result = await self.db.scalars(
            select(Category)
            .where(Category.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )

        return result.all()

    async def get_by_name(self, name: str) -> Category | None:
        return await self.db.scalar(
            select(Category).where(Category.name == name)
        )

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.db.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
        )

    async def get_by_id_including_inactive(
            self,
            category_id: int,
    ) -> Category | None:
        return await self.db.scalar(
            select(Category).where(Category.id == category_id)
        )

    async def create(self, name: str) -> Category:
        """
        Создаёт новую категорию.
        """
        db_category = Category(name=name)

        self.db.add(db_category)
        await self.db.flush()

        return db_category

    async def update(
        self, category_id: int, new_name: str,
    ) -> Category | None:
        """
        Обновляет название активной категории.
        """
        db_category = await self.db.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
        )

        if db_category is None:
            return None

        db_category.name = new_name

        return db_category

    async def activate(self, category_id: int) -> Category | None:
        """
        Повторно активирует категорию.
        """
        db_category = await self.db.scalar(
            select(Category).where(Category.id == category_id)
        )

        if db_category is None:
            return None

        db_category.is_active = True

        return db_category

    async def delete(self, category_id: int) -> Category | None:
        """
        Выполняет мягкое удаление категории.
        """
        db_category = await self.db.scalar(
            select(Category).where(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
        )

        if db_category is None:
            return None

        db_category.is_active = False

        return db_category

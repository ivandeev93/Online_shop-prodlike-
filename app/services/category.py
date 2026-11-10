from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.category import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
)
from app.models.categories import Category
from app.repositories.category import CategoryRepository
from app.schemas import CategoryCreate


class CategoryService:

    def __init__(
        self,
        category_repo: CategoryRepository,
        db: AsyncSession,
    ):
        self.category_repo = category_repo
        self.db = db

    async def get_all_categories(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Category]:
        """
        Возвращает список активных категорий.
        """
        return await self.category_repo.get_all(
            skip=skip,
            limit=limit,
        )

    async def get_category_by_id(self, category_id: int) -> Category:
        """
        Возвращает активную категорию по ID.
        """
        category = await self.category_repo.get_by_id(category_id)

        if category is None:
            raise CategoryNotFoundError(
                f"Category with ID {category_id} not found"
            )

        return category

    async def activate_category(self, category_id: int) -> Category:
        """
        Повторно активирует категорию.
        """
        try:
            category = await self.category_repo.get_by_id_including_inactive(
                category_id
            )

            if category is None:
                raise CategoryNotFoundError(
                    f"Category with ID {category_id} not found"
                )

            existing_category = await self.category_repo.get_by_name(
                category.name
            )

            if (
                    existing_category is not None
                    and existing_category.id != category_id
            ):
                raise CategoryAlreadyExistsError(
                    f"Category with name {category.name} already exists"
                )

            result = await self.category_repo.activate(category_id)

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def create_category(self, category: CategoryCreate) -> Category:
        """
        Создаёт новую категорию.
        """
        try:
            existing_category = await self.category_repo.get_by_name(
                category.name
            )

            if existing_category is not None:
                raise CategoryAlreadyExistsError(
                    f"Category with name {category.name} already exists"
                )

            result = await self.category_repo.create(category.name)

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def update_category(
        self,
        category: CategoryCreate,
        category_id: int,
    ) -> Category:
        """
        Обновляет название активной категории.
        """
        try:
            category_with_same_name = await self.category_repo.get_by_name(
                category.name
            )

            if (
                category_with_same_name is not None
                and category_with_same_name.id != category_id
            ):
                raise CategoryAlreadyExistsError(
                    f"Category with name {category.name} already exists"
                )

            result = await self.category_repo.update(
                category_id=category_id,
                new_name=category.name,
            )

            if result is None:
                raise CategoryNotFoundError(
                    f"Category with ID {category_id} not found"
                )

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def delete_category(self, category_id: int) -> Category:
        """
        Выполняет мягкое удаление категории.
        """
        try:
            result = await self.category_repo.delete(category_id)

            if result is None:
                raise CategoryNotFoundError(
                    f"Category with ID {category_id} not found"
                )

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

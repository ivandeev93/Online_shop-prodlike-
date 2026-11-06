from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category import CategoryRepository
from app.models.categories import Category
from app.schemas import CategoryCreate
from app.exceptions.category import CategoryNotFoundError, CategoryAlreadyExistsError


class CategoryService:

    def __init__(self, category_repo: CategoryRepository, db: AsyncSession):
        self.category_repo = category_repo
        self.db = db

    async def get_all_categories(
            self, skip: int = 0, limit: int = 100
    ) -> Sequence[Category]:
        return await self.category_repo.get_all(skip=skip, limit=limit)

    async def get_category_by_id(self, category_id: int) -> Category:
        result = await self.category_repo.get_by_id(category_id)

        if result is None:
            raise CategoryNotFoundError(
                f"Category with ID {category_id} not found"
            )

        return result

    async def activate_category(self, category_id: int) -> Category:
        try:
            result = await self.category_repo.activate(category_id)

            if result is None:
                raise CategoryNotFoundError(
                    f"Category with ID {category_id} not found"
                )

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def create_category(self, category: CategoryCreate) -> Category:
        try:
            existing_category = await self.category_repo.get_by_name(category.name)

            if existing_category:
                raise CategoryAlreadyExistsError(
                    f"Category with name {category.name} already exists"
                )

            result = await self.category_repo.create(category.name)

            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def update_category(self, category: CategoryCreate,
                              category_id: int) -> Category:
        try:
            category_with_same_name = await self.category_repo.get_by_name(category.name)

            if (category_with_same_name
                and category_with_same_name.id != category_id
            ):
                raise CategoryAlreadyExistsError(
                    f"Category with name {category.name} already exists"
                )

            result = await self.category_repo.update(category_id=category_id,
                                                     new_name=category.name)

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

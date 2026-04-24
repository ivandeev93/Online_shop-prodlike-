# CategoryRepository
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.categories import Category
from app.schemas import CategoryCreate



class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        result = await self.db.scalars(select(Category).where(Category.is_active == True).offset(skip).limit(limit))
        return result.all()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.scalar(select(Category).where(Category.name == name))
        return result

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.db.scalar(select(Category).where(Category.id == category_id, Category.is_active == True))

    async def create(self, category: CategoryCreate) -> Category:
        # Создание новой категории
        db_category = Category(**category.model_dump())
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def update(self, category_id: int, category: CategoryCreate):
        # Проверяем существование категории
        stmt = select(Category).where(Category.id == category_id,
                                           Category.is_active == True)
        result = await self.db.scalars(stmt)
        db_category = result.first()
        if not db_category:
            return None

        # Проверяем parent_id, если указан
        if category.parent_id is not None:
            parent_stmt = select(Category).where(Category.id == category.parent_id,
                                                      Category.is_active == True)
            parent_result = await self.db.scalars(parent_stmt)
            parent = parent_result.first()
            if not parent:
                return None
            if parent.id == category_id:
                return None

        # Обновляем категорию
        update_data = category.model_dump(exclude_unset=True)
        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**update_data)
        )
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def delete(self, category_id: int):
        # Проверяем существование категории
        stmt = select(Category).where(Category.id == category_id, Category.is_active == True)
        result = await self.db.scalars(stmt)
        db_category = result.first()
        if not db_category:
            return None

        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(is_active=False)
        )
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category
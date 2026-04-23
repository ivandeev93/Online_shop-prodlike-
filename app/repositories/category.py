# CategoryRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.categories import Category



class CategoryRepository:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
        result = await db.scalars(select(Category).offset(skip).limit(limit))
        return result.all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Category | None:
        result = await db.scalar(select(Category).filter(Category.name == name))
        return result

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int):
        return await db.scalar(select(Category).filter(Category.id == category_id))

    @staticmethod
    async def create(db: AsyncSession, name: str) -> Category:
        db_category = Category(name=name)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def update(db: AsyncSession, name: str):
        pass
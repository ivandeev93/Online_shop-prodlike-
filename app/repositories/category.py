# CategoryRepository
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from app.models.categories import Category
from app.schemas import CategoryCreate



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
    async def create(db: AsyncSession, category: CategoryCreate) -> Category:
        # Проверка существования parent_id, если указан
        if category.parent_id is not None:
            stmt = select(Category).where(Category.id == category.parent_id,
                                               Category.is_active == True)
            result = await db.scalars(stmt)
            parent = result.first()
            if parent is None:
                raise HTTPException(status_code=400, detail="Parent category not found")

        # Создание новой категории
        db_category = Category(**category.model_dump())
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def update(db: AsyncSession, category_id: int, category: CategoryCreate):
        # Проверяем существование категории
        stmt = select(Category).where(Category.id == category_id,
                                           Category.is_active == True)
        result = await db.scalars(stmt)
        db_category = result.first()
        if not db_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Проверяем parent_id, если указан
        if category.parent_id is not None:
            parent_stmt = select(Category).where(Category.id == category.parent_id,
                                                      Category.is_active == True)
            parent_result = await db.scalars(parent_stmt)
            parent = parent_result.first()
            if not parent:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent category not found")
            if parent.id == category_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent")

        # Обновляем категорию
        update_data = category.model_dump(exclude_unset=True)
        await db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**update_data)
        )
        await db.commit()
        return db_category

    @staticmethod
    async def delete(db: AsyncSession, category_id: int):
        # Проверяем существование категории
        stmt = select(Category).where(Category.id == category_id, Category.is_active == True)
        result = await db.scalars(stmt)
        db_category = result.first()
        if not db_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        await db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(is_active=False)
        )
        await db.commit()
        return db_category
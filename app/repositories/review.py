from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Review]:
        """Получает все активные отзывы."""

        result = await self.db.scalars(
            select(Review).where(
                Review.is_active.is_(True)
            )
        )

        return result.all()

    async def get_by_product(
        self,
        product_id: int,
    ) -> Sequence[Review]:
        """Получает все активные отзывы указанного товара."""

        result = await self.db.scalars(
            select(Review)
            .where(
                Review.product_id == product_id,
                Review.is_active.is_(True),
            )
        )

        return result.all()

    async def get_by_id(
        self,
        review_id: int,
    ) -> Review | None:
        """Получает активный отзыв по ID."""

        return await self.db.scalar(
            select(Review).where(
                Review.id == review_id,
                Review.is_active.is_(True),
            )
        )

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
    ) -> Review | None:
        """
        Проверяет, оставлял ли пользователь отзыв о товаре.

        Проверяем и неактивные записи, поскольку пара
        user_id + product_id уникальна в базе данных.
        """

        return await self.db.scalar(
            select(Review).where(
                Review.user_id == user_id,
                Review.product_id == product_id,
            )
        )

    async def create(
        self,
        product_id: int,
        user_id: int,
        grade: int,
        comment: str | None = None,
    ) -> Review:
        """Создаёт отзыв."""

        db_review = Review(
            product_id=product_id,
            user_id=user_id,
            grade=grade,
            comment=comment,
        )

        self.db.add(db_review)
        await self.db.flush()

        return db_review

    async def delete(
        self,
        review_id: int,
    ) -> Review | None:
        """Выполняет мягкое удаление отзыва."""

        db_review = await self.get_by_id(review_id)

        if db_review is None:
            return None

        db_review.is_active = False

        await self.db.flush()

        return db_review

    async def get_average_grade(
        self,
        product_id: int,
    ) -> Decimal:
        """Вычисляет среднюю оценку активных отзывов."""

        average = await self.db.scalar(
            select(func.avg(Review.grade)).where(
                Review.product_id == product_id,
                Review.is_active.is_(True),
            )
        )

        if average is None:
            return Decimal("0.00")

        return Decimal(str(average)).quantize(
            Decimal("0.01")
        )

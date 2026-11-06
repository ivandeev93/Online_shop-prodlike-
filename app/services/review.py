from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.product import ProductNotFoundError
from app.exceptions.review import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
    ReviewPermissionDeniedError,
)
from app.models.reviews import Review
from app.models.users import User
from app.repositories.product import ProductRepository
from app.repositories.review import ReviewRepository
from app.schemas import ReviewCreate


class ReviewService:

    def __init__(
        self,
        review_repo: ReviewRepository,
        product_repo: ProductRepository,
        db: AsyncSession,
    ):
        self.review_repo = review_repo
        self.product_repo = product_repo
        self.db = db

    async def get_all_reviews(self) -> Sequence[Review]:
        """
        Возвращает все активные отзывы.
        """
        return await self.review_repo.get_all()

    async def get_reviews_by_product(
        self,
        product_id: int,
    ) -> Sequence[Review]:
        """
        Возвращает активные отзывы указанного товара.
        """
        product = await self.product_repo.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundError()

        return await self.review_repo.get_by_product(product_id)

    async def create_review(
        self,
        review: ReviewCreate,
        current_user: User,
    ) -> Review:
        """
        Создаёт отзыв от имени текущего покупателя.
        """
        if current_user.role != "buyer":
            raise ReviewPermissionDeniedError(
                "Only buyers can create reviews"
            )

        try:
            # Блокируем товар до завершения создания отзыва и пересчёта рейтинга.
            product = await self.product_repo.get_by_id_for_update(
                review.product_id
            )

            if product is None or not product.is_active:
                raise ProductNotFoundError()

            # Проверяем наличие любого отзыва, включая неактивный.
            existing_review = (
                await self.review_repo.get_by_user_and_product(
                    user_id=current_user.id,
                    product_id=review.product_id,
                )
            )

            if existing_review is not None:
                raise ReviewAlreadyExistsError()

            db_review = await self.review_repo.create(
                product_id=review.product_id,
                user_id=current_user.id,
                grade=review.grade,
                comment=review.comment,
            )

            # Пересчитываем рейтинг с учётом нового отзыва.
            average_grade = await self.review_repo.get_average_grade(
                review.product_id
            )

            await self.product_repo.update_rating(
                product_id=review.product_id,
                rating=average_grade,
            )

            await self.db.commit()
            await self.db.refresh(db_review)

            return db_review

        except Exception:
            await self.db.rollback()
            raise

    async def delete_review(
        self,
        review_id: int,
        current_user: User,
    ) -> dict[str, str]:
        """
        Выполняет мягкое удаление отзыва.
        """
        try:
            db_review = await self.review_repo.get_by_id(review_id)

            if db_review is None:
                raise ReviewNotFoundError()

            # Удалять отзыв может его автор или администратор.
            if (
                db_review.user_id != current_user.id
                and current_user.role != "admin"
            ):
                raise ReviewPermissionDeniedError()

            product_id = db_review.product_id

            # Блокируем товар, чтобы согласовать пересчёт рейтинга.
            product = await self.product_repo.get_by_id_for_update(
                product_id
            )

            if product is None:
                raise ProductNotFoundError()

            # Повторно проверяем отзыв после получения блокировки.
            db_review = await self.review_repo.get_by_id(review_id)

            if db_review is None:
                raise ReviewNotFoundError()

            deleted_review = await self.review_repo.delete(review_id)

            if deleted_review is None:
                raise ReviewNotFoundError()

            # Пересчитываем рейтинг без удалённого отзыва.
            average_grade = await self.review_repo.get_average_grade(
                product_id
            )

            await self.product_repo.update_rating(
                product_id=product_id,
                rating=average_grade,
            )

            await self.db.commit()

            return {"message": "Review deleted"}

        except Exception:
            await self.db.rollback()
            raise

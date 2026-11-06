from fastapi import APIRouter, Depends, status

from app.auth import get_current_admin, get_current_buyer
from app.core.dependencies import get_review_service
from app.models.users import User
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.services.review import ReviewService


router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_reviews(
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Возвращает список всех активных отзывов.
    """
    return await review_service.get_all_reviews()


@router.get(
    "/products/{product_id}/reviews/",
    response_model=list[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_product(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Возвращает активные отзывы указанного товара.
    """
    return await review_service.get_reviews_by_product(product_id)


@router.post(
    "/reviews/",
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_buyer),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Создаёт отзыв от имени текущего покупателя.
    """
    return await review_service.create_review(
        review=review,
        current_user=current_user,
    )


@router.delete("/reviews/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_admin),
    review_service: ReviewService = Depends(get_review_service),
):
    """
    Выполняет мягкое удаление отзыва (только для администратора).
    """
    return await review_service.delete_review(
        review_id=review_id,
        current_user=current_user,
    )

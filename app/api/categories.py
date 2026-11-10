from fastapi import APIRouter, Depends, Query, status

from app.auth import get_current_admin
from app.core.dependencies import get_category_service
from app.models.users import User
from app.schemas import Category, CategoryCreate
from app.services.category import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[Category])
async def get_all_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Возвращает список всех активных категорий.
    """
    return await category_service.get_all_categories(
        skip=skip,
        limit=limit,
    )


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Создаёт новую категорию. Доступно только администратору.
    """
    return await category_service.create_category(category=category)


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Обновляет категорию. Доступно только администратору.
    """
    return await category_service.update_category(
        category=category,
        category_id=category_id,
    )


@router.patch("/{category_id}/activate", response_model=Category)
async def activate_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Восстанавливает категорию. Доступно только администратору.
    """
    return await category_service.activate_category(category_id)


@router.delete("/{category_id}", response_model=Category)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_admin),
):
    """
    Выполняет мягкое удаление категории. Доступно только администратору.
    """
    return await category_service.delete_category(category_id)

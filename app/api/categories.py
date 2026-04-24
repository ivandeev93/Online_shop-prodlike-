from fastapi import APIRouter, Depends, HTTPException, status


from app.core.dependencies import get_category_service
from app.schemas import Category, CategoryCreate
from app.services.category import CategoryService


# Создаём маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

# ПЕРЕДЕЛАТЬ ИСКЛЮЧЕНИЯ С ОТДЕЛЬНЫМИ КЛАССАМИ ИСКЛЮЧЕНИЙ В СЕРВИСНОМ СЛОЕ
@router.get("/", response_model=list[Category])
async def get_all_categories(
        skip: int = 0,
        limit: int = 100,
        category_service: CategoryService = Depends(get_category_service)  # Инъекция сервиса
):
    """
    Возвращает список всех активных категорий.
    """
    categories = await category_service.get_all_categories(skip=skip, limit=limit)
    return categories


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
        category: CategoryCreate,
        category_service: CategoryService = Depends(get_category_service)  # Инъекция сервиса
):
    """
    Создаёт новую категорию.
    """
    db_category = await category_service.create_category(category=category)
    if db_category is None:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    return db_category



@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: int, category: CategoryCreate,
                          category_service: CategoryService = Depends(get_category_service)):
    """
    Обновляет категорию по её ID.
    """
    db_category = await category_service.update_category(category, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_category


@router.delete("/{category_id}", response_model=Category)
async def delete_category(category_id: int, category_service: CategoryService = Depends(get_category_service)):
    """
    Выполняет мягкое удаление категории по её ID, устанавливая is_active = False.
    """
    db_category = await category_service.delete_category(category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_category

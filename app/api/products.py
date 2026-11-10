from decimal import Decimal
import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.auth import get_current_seller, get_current_user
from app.core.dependencies import (
    get_category_service,
    get_product_service,
)
from app.core.media import (
    remove_product_image,
    save_product_image,
)
from app.models.users import User as UserModel
from app.schemas import (
    Product as ProductSchema,
    ProductCreate,
    ProductList,
    ProductUpdate,
)
from app.services.category import CategoryService
from app.services.product import ProductService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductList)
async def get_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: int | None = Query(None, ge=1),
    search: str | None = Query(
        None,
        min_length=1,
        description="Search by product name or description",
    ),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    in_stock: bool | None = Query(
        None,
        description="true — products in stock, false — products out of stock",
    ),
    seller_id: int | None = Query(None, ge=1),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Возвращает список активных товаров.
    """
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )

    items, total = await product_service.get_all_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        seller_id=seller_id,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/category/{category_id}", response_model=ProductList)
async def get_products_by_category(
    category_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_service: ProductService = Depends(get_product_service),
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Возвращает список активных товаров в указанной категории по её ID.
    """
    # Проверяем, что категория существует и активна.
    await category_service.get_category_by_id(category_id)

    items, total = await product_service.get_all_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    return await product_service.get_product_by_id(product_id)


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate = Depends(ProductCreate.as_form),
    image: UploadFile | None = File(None),
    product_service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_seller),
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    image_url = None

    try:
        if image is not None:
            image_url = await save_product_image(image)

        return await product_service.create_product(
            product=product,
            current_user=current_user,
            image_url=image_url,
        )

    except Exception:
        if image_url:
            try:
                remove_product_image(image_url)
            except OSError:
                logger.exception(
                    "Failed to remove uploaded product image: %s",
                    image_url,
                )
        raise


@router.patch("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    updated_product, _ = await product_service.update_product(
        product_id=product_id,
        product=product,
        current_user=current_user,
    )

    return updated_product


@router.put("/{product_id}/image", response_model=ProductSchema)
async def update_product_image(
    product_id: int,
    image: UploadFile = File(...),
    product_service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Обновляет изображение товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    new_image_url = None

    try:
        new_image_url = await save_product_image(image)

        updated_product, old_image_url = (
            await product_service.update_product(
                product_id=product_id,
                product=ProductUpdate(),
                current_user=current_user,
                image_url=new_image_url,
            )
        )

    except Exception:
        if new_image_url:
            try:
                remove_product_image(new_image_url)
            except OSError:
                logger.exception(
                    "Failed to remove uploaded product image: %s",
                    new_image_url,
                )
        raise

    # Старое изображение удаляем только после успешного commit.
    if old_image_url:
        try:
            remove_product_image(old_image_url)
        except OSError:
            logger.exception(
                "Failed to remove old product image: %s",
                old_image_url,
            )

    return updated_product


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    return await product_service.delete_product(
        product_id=product_id,
        current_user=current_user,
    )

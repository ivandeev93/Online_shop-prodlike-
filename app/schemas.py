from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from pydantic import computed_field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Annotated

from fastapi import Form



class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=50,
                      description="Название категории (3-50 символов)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Category name must contain at least 3 characters")

        return value


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")
    is_active: bool = Field(description="Активность категории")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: str | None = Field(default=None, max_length=500,
                                       description="Описание товара (до 500 символов)")
    price: Decimal = Field(gt=0, description="Цена товара (больше 0)", decimal_places=2)
    stock: int = Field(ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(gt=0, description="ID категории, к которой относится товар")

    @classmethod
    def as_form(
            cls,
            name: Annotated[str, Form(...)],
            price: Annotated[Decimal, Form(...)],
            stock: Annotated[int, Form(...)],
            category_id: Annotated[int, Form(...)],
            description: Annotated[Optional[str], Form()] = None,
    ) -> "ProductCreate":
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )


class ProductUpdate(BaseModel):
    """
    Схема для частичного обновления товара.
    """
    name: str | None = Field(default=None, min_length=3,
                             max_length=100, description="Название товара")
    description: str | None = Field(default=None, max_length=500, description="Описание товара")
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2, description="Цена товара")
    stock: int | None = Field(default=None, ge=0, description="Количество товара на складе")
    category_id: int | None = Field(default=None, gt=0, description="ID категории")

    @field_validator(
        "name",
        "price",
        "stock",
        "category_id",
        mode="before",
    )
    @classmethod
    def prevent_null_values(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")

        return value


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(description="Цена товара", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    is_active: bool = Field(description="Активность товара")
    rating: Decimal = Field(ge=0, le=5, description="Средний рейтинг товара")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для регистрации пользователя.
    """
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(
        min_length=8,
        description="Пароль (минимум 8 символов, максимум 72 байта в UTF-8)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        """
        Проверяет максимальную длину пароля для bcrypt.
        """
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes in UTF-8")

        return value


class User(BaseModel):
    """
    Модель для ответа пользователя.
    """
    id: int = Field(description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(description="Email пользователя")
    is_active: bool = Field(description="Активность пользователя")
    role: str = Field(description="Роль пользователя")

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Модель для создания токена доступа и рефреш токена.
    """
    access_token: str = Field(description="Токен доступа")
    refresh_token: str = Field(description="Рефреш токен")
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Модель для возврата рефреш токена.
    """
    refresh_token: str


class ReviewCreate(BaseModel):
    """
    Модель для создания и обновления отзыва.
    Используется в POST запросах
    """
    product_id: int = Field(gt=0, description="Уникальный идентификатор товара")
    comment: str | None = Field(default=None, max_length=2000, description="Текст отзыва")
    grade: int = Field(ge=1, le=5, description="Оценка товара от 1 до 5")


class Review(BaseModel):
    """
    Модель для ответа с данными отзыва.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="Уникальный идентификатор пользователя")
    product_id: int = Field(description="Уникальный идентификатор товара")
    comment: str | None = Field(None, description="Текст отзыва")
    comment_date: datetime = Field(description="Время создания отзыва")
    grade: int = Field(ge=1, le=5,description="Оценка товара от 1 до 5")
    is_active: bool = Field(description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """
    Список пагинации для товаров.
    """
    items: list[Product] = Field(description="Товары для текущей страницы")
    total: int = Field(ge=0, description="Общее количество товаров")
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов


class CartItemBase(BaseModel):
    """
    Базовая модель позиции корзины.
    """
    product_id: int = Field(gt=0, description="ID товара")
    quantity: int = Field(ge=1, description="Количество товара")


class CartItemCreate(CartItemBase):
    """
    Модель для добавления нового товара в корзину.
    """
    pass


class CartItemUpdate(BaseModel):
    """Модель для обновления количества товара в корзине."""
    quantity: int = Field(..., ge=1, description="Новое количество товара")


class CartItem(BaseModel):
    """Товар в корзине с данными продукта."""
    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(..., ge=1, description="Количество товара")
    product: Product = Field(..., description="Информация о товаре")

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """
    Полная информация о корзине пользователя.
    """
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItem] = Field(default_factory=list, description="Содержимое корзины")
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    """
    Модель позиции заказа.
    """
    id: int = Field(..., description="ID позиции заказа")
    product_id: int | None = Field(None, description="ID товара")
    quantity: int = Field(ge=1, description="Количество")
    unit_price: Decimal = Field(ge=0, description="Цена за единицу на момент покупки")
    product: Product | None = Field(None, description="Полная информация о товаре")

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def total_price(self) -> Decimal:
        """Рассчитывает общую стоимость позиции заказа."""
        return self.unit_price * self.quantity


class Order(BaseModel):
    """
    Модель заказа.
    """
    id: int = Field(description="ID заказа")
    user_id: int = Field(..., description="ID пользователя")
    status: str = Field(..., description="Текущий статус заказа")
    total_amount: Decimal = Field(..., ge=0, description="Общая стоимость")
    created_at: datetime = Field(..., description="Когда заказ был создан")
    updated_at: datetime = Field(..., description="Когда последний раз обновлялся")
    items: list[OrderItem] = Field(default_factory=list, description="Список позиций")

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    """
    Модель списка заказов с пагинацией.
    """
    items: list[Order] = Field(description="Заказы на текущей странице")
    total: int = Field(ge=0, description="Общее количество заказов")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, description="Размер страницы")

    model_config = ConfigDict(from_attributes=True)

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import cart, categories, orders, products, reviews, users
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается. Создаем базу данных...")
    await create_db_and_tables()
    print("База данных инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    title="Онлайн магазин на FastAPI с SQLAlchemy 2.0",
    lifespan=lifespan
)

# Подключение обработчиков маршрутов
app.include_router(cart.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Онлайн магазин"}
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import cart, categories, orders, products, reviews, users
from app.core.database import close_database_connection



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается.")

    try:
        yield
    finally:
        await close_database_connection()
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
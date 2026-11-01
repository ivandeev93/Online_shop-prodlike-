from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings



engine = create_async_engine(
    settings.database_url,
    echo=True,        # True для отладки
    pool_size=10,
    max_overflow=20
)

# Base для декларативного определения моделей
class Base(DeclarativeBase):
    pass

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Функция закрытия соединений engine
async def close_database_connection():
    await engine.dispose()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

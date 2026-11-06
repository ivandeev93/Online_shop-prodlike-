from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(
            self,
            email: str,
    ) -> User | None:
        # Получение пользователя по email
        result = await self.db.scalar(select(User).where(User.email == email))

        return result

    async def get_by_id(
            self,
            user_id: int,
    ) -> User | None:
        # Получение пользователя по ID
        result = await self.db.scalar(select(User).where(User.id == user_id))

        return result

    async def create(
            self,
            email: str,
            hashed_password: str,
            role: str = "buyer",
    ) -> User:
        # Создание нового пользователя
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            role=role
        )

        self.db.add(db_user)
        await self.db.flush()

        return db_user

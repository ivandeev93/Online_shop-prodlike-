from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import (
    UnauthorizedUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.users import User
from app.repositories.user import UserRepository
from app.schemas import UserCreate
from app.core.security import hash_password, verify_password


class UserService:

    def __init__(
        self,
        user_repo: UserRepository,
        db: AsyncSession,
    ):
        self.user_repo = user_repo
        self.db = db

    async def register_user(self, user: UserCreate) -> User:
        # Проверяем, зарегистрирован ли пользователь с таким email
        registered_user = await self.user_repo.get_by_email(user.email)

        if registered_user:
            raise UserAlreadyExistsError(
                "User with this email already registered"
            )

        try:
            # Хешируем пароль перед сохранением
            hashed_password = hash_password(user.password)

            # Создаём пользователя
            new_user = await self.user_repo.create(
                email=user.email,
                hashed_password=hashed_password,
            )

            await self.db.commit()

            return new_user

        except Exception:
            await self.db.rollback()
            raise

    async def authenticate_user(
        self,
        email: str,
        plain_password: str,
    ) -> User:
        # Ищем пользователя по email
        user = await self.user_repo.get_by_email(email)

        # Проверяем существование, активность и правильность пароля
        if (
            user is None
            or not user.is_active
            or not verify_password(plain_password, user.hashed_password)
        ):
            raise UnauthorizedUserError("Incorrect email or password")

        return user

    async def get_user_by_id(self, user_id: int) -> User:

        result = await self.user_repo.get_by_id(user_id)

        if result is None:
            raise UserNotFoundError(
                f"User with id {user_id} not found"
            )

        return result

    async def get_user_by_email(self, email: str) -> User:

        result = await self.user_repo.get_by_email(email)

        if result is None:
            raise UserNotFoundError(
                f"User with email {email} not found"
            )

        return result

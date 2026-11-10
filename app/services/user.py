import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
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
        """
        Регистрирует нового пользователя.
        """
        registered_user = await self.user_repo.get_by_email(user.email)

        if registered_user:
            raise UserAlreadyExistsError(
                "User with this email already registered"
            )

        try:
            # Хешируем пароль в отдельном потоке, не блокируя event loop.
            hashed_password = await asyncio.to_thread(
                hash_password,
                user.password,
            )

            new_user = await self.user_repo.create(
                email=user.email,
                hashed_password=hashed_password,
            )

            await self.db.commit()

            return new_user

        except IntegrityError as exc:
            await self.db.rollback()

            raise UserAlreadyExistsError(
                "User with this email already registered"
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    async def authenticate_user(
        self,
        email: str,
        plain_password: str,
    ) -> User:
        """
        Проверяет учетные данные пользователя.
        """
        user = await self.user_repo.get_by_email(email)

        if user is None or not user.is_active:
            raise UnauthorizedUserError("Incorrect email or password")

        # Проверяем пароль в отдельном потоке.
        password_is_valid = await asyncio.to_thread(
            verify_password,
            plain_password,
            user.hashed_password,
        )

        if not password_is_valid:
            raise UnauthorizedUserError("Incorrect email or password")

        return user

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Возвращает пользователя по ID.
        """
        result = await self.user_repo.get_by_id(user_id)

        if result is None:
            raise UserNotFoundError(
                f"User with id {user_id} not found"
            )

        return result

    async def get_user_by_email(self, email: str) -> User:
        """
        Возвращает пользователя по email.
        """
        result = await self.user_repo.get_by_email(email)

        if result is None:
            raise UserNotFoundError(
                f"User with email {email} not found"
            )

        return result

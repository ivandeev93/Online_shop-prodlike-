from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import get_async_db
from app.models.users import User


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT доступа.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "token_type": "access",
    })

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(data: dict) -> str:
    """
    Создаёт рефреш токен.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(
    token: str,
    expected_type: str,
) -> dict:
    """
    Декодирует JWT и проверяет его тип.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        if payload.get("token_type") != expected_type:
            raise credentials_exception

        if not payload.get("sub"):
            raise credentials_exception

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise credentials_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Проверяет токен доступа и возвращает текущего пользователя.
    """
    payload = decode_token(
        token=token,
        expected_type="access",
    )

    email = payload["sub"]

    user = await db.scalar(
        select(User).where(
            User.email == email,
            User.is_active.is_(True),
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_seller(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, является ли текущий пользователь продавцом.
    """
    if current_user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action",
        )

    return current_user


async def get_current_buyer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, является ли текущий пользователь покупателем.
    """
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can perform this action",
        )

    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, является ли текущий пользователь администратором.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )

    return current_user

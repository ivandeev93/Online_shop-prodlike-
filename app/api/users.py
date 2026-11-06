from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import (
    UserCreate,
    User as UserSchema,
    Token,
    RefreshTokenRequest,
)
from app.services.user import UserService
from app.core.dependencies import get_user_service
from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Регистрация нового пользователя.
    """
    return await user_service.register_user(user)


@router.post("/token", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    """
    Аутентификация пользователя и возврат JWT токена.
    """
    user = await user_service.authenticate_user(
        email=form_data.username,
        plain_password=form_data.password,
    )

    token_data = {
        "sub": user.email,
        "id": user.id,
        "role": user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Обновление токена доступа с помощью рефреш токена.
    """
    payload = decode_token(
        token=token_data.refresh_token,
        expected_type="refresh",
    )

    email = payload["sub"]

    user = await user_service.get_user_by_email(email)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_access_token = create_access_token({
        "sub": user.email,
        "id": user.id,
        "role": user.role,
    })

    return Token(
        access_token=new_access_token,
        refresh_token=token_data.refresh_token,
    )

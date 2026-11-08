from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

import asyncio
import uuid
import warnings
from io import BytesIO
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

MEDIA_DIR = BASE_DIR / "media"
MEDIA_ROOT = MEDIA_DIR / "products"

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_SIZE = 2 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": {
        "extension": ".jpg",
        "format": "JPEG",
    },
    "image/png": {
        "extension": ".png",
        "format": "PNG",
    },
    "image/webp": {
        "extension": ".webp",
        "format": "WEBP",
    },
}


def validate_image_content(content: bytes, content_type: str) -> bool:
    """
    Проверяет фактический формат изображения и возможность его декодирования.
    """
    allowed_type = ALLOWED_IMAGE_TYPES.get(content_type)

    if allowed_type is None:
        return False

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(content)) as image:
                if image.format != allowed_type["format"]:
                    return False

                image.verify()

            # Повторно открываем файл, чтобы проверить возможность декодирования.
            with Image.open(BytesIO(content)) as image:
                image.load()

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        ValueError,
    ):
        return False

    return True


async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара.
    Возвращает относительный URL сохранённого файла.
    """
    try:
        content_type = file.content_type

        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, PNG or WebP images are allowed",
            )

        content = await file.read(MAX_IMAGE_SIZE + 1)

        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image is too large. Maximum size is 2 MB",
            )

        if not validate_image_content(content, content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file",
            )

        extension = ALLOWED_IMAGE_TYPES[content_type]["extension"]
        file_name = f"{uuid.uuid4()}{extension}"
        file_path = MEDIA_ROOT / file_name

        await asyncio.to_thread(file_path.write_bytes, content)

        return f"/media/products/{file_name}"

    finally:
        await file.close()


def remove_product_image(url: str | None) -> None:
    """
    Удаляет изображение товара, если файл существует.
    """
    if not url:
        return

    prefix = "/media/products/"

    if not url.startswith(prefix):
        return

    file_name = url.removeprefix(prefix)

    # Не позволяем использовать пути с переходом в другие директории.
    if not file_name or Path(file_name).name != file_name:
        return

    file_path = MEDIA_ROOT / file_name
    file_path.unlink(missing_ok=True)
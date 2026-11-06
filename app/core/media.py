
from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile, status


BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_ROOT = BASE_DIR / "media" / "products"

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_SIZE = 2 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": (".jpg",),
    "image/png": (".png",),
    "image/webp": (".webp",),
}


def validate_image_content(content: bytes, content_type: str) -> bool:
    """Проверяет фактический формат изображения по сигнатуре файла."""

    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")

    if content_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")

    if content_type == "image/webp":
        return (
            len(content) >= 12
            and content[:4] == b"RIFF"
            and content[8:12] == b"WEBP"
        )

    return False


async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара.
    Возвращает относительный URL сохранённого файла.
    """

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

    extension = ALLOWED_IMAGE_TYPES[content_type][0]
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name

    file_path.write_bytes(content)

    return f"/media/products/{file_name}"


def remove_product_image(url: str | None) -> None:
    """Удаляет изображение товара, если файл существует."""

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

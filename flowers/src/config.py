"""Загрузка настроек из окружения / .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

THREADS_USER_ID = os.getenv("THREADS_USER_ID", "").strip()
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "").strip()
THREADS_APP_SECRET = os.getenv("THREADS_APP_SECRET", "").strip()

# Базовый URL, куда выложены картинки из папки images/.
# Напр.: https://raw.githubusercontent.com/<user>/<repo>/main/images
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "").strip().rstrip("/")

DRY_RUN = os.getenv("DRY_RUN", "true").strip().lower() in ("1", "true", "yes")

# Пауза между созданием контейнера и публикацией (Meta рекомендует подождать).
PUBLISH_DELAY_SECONDS = int(os.getenv("PUBLISH_DELAY_SECONDS", "5"))


def image_url(filename: str) -> str:
    if not filename:
        return ""
    if filename.startswith("http://") or filename.startswith("https://"):
        return filename
    if not IMAGE_BASE_URL:
        raise SystemExit(
            f"Пост требует картинку ({filename}), но IMAGE_BASE_URL не задан в .env."
        )
    return f"{IMAGE_BASE_URL}/{filename}"


def require_credentials() -> None:
    missing = [
        name
        for name, value in {
            "THREADS_USER_ID": THREADS_USER_ID,
            "THREADS_ACCESS_TOKEN": THREADS_ACCESS_TOKEN,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(
            "Не заданы переменные: " + ", ".join(missing) + ". Заполни .env (см. .env.example)."
        )

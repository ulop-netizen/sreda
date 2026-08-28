"""Проверка токена из .env: кто я, какой user_id. Дописывает THREADS_USER_ID в .env."""
import re
from pathlib import Path

import requests

from src import config

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def main() -> None:
    token = config.THREADS_ACCESS_TOKEN
    if not token:
        raise SystemExit("В .env пустой THREADS_ACCESS_TOKEN. Вставь токен и сохрани файл.")

    resp = requests.get(
        "https://graph.threads.net/v1.0/me",
        params={"fields": "id,username", "access_token": token},
        timeout=30,
    )
    data = resp.json()
    if resp.status_code >= 400 or "error" in data:
        raise SystemExit(f"Токен не принят: {resp.status_code} {data}")

    user_id, username = data["id"], data.get("username", "?")
    print(f"OK: @{username}  user_id={user_id}")

    text = ENV.read_text(encoding="utf-8")
    text = re.sub(r"^THREADS_USER_ID=.*$", f"THREADS_USER_ID={user_id}", text, flags=re.M)
    ENV.write_text(text, encoding="utf-8")
    print("THREADS_USER_ID записан в .env")


if __name__ == "__main__":
    main()

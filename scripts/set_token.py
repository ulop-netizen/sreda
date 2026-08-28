"""Спрашивает токен (скрытый ввод), проверяет его, пишет в .env токен и user_id."""
import re
from getpass import getpass
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def upsert(text: str, key: str, value: str) -> str:
    line = f"{key}={value}"
    if re.search(rf"^{key}=.*$", text, flags=re.M):
        return re.sub(rf"^{key}=.*$", line, text, flags=re.M)
    return text.rstrip() + "\n" + line + "\n"


def main() -> None:
    token = getpass("Вставь токен Threads и нажми Enter (ввод не отображается): ").strip()
    if not token:
        raise SystemExit("Пусто.")

    resp = requests.get(
        "https://graph.threads.net/v1.0/me",
        params={"fields": "id,username", "access_token": token},
        timeout=30,
    )
    data = resp.json()
    if resp.status_code >= 400 or "error" in data:
        raise SystemExit(f"Токен не принят: {resp.status_code} {data}")

    text = ENV.read_text(encoding="utf-8") if ENV.exists() else ""
    text = upsert(text, "THREADS_ACCESS_TOKEN", token)
    text = upsert(text, "THREADS_USER_ID", data["id"])
    ENV.write_text(text, encoding="utf-8")

    print(f"OK: @{data.get('username','?')}  user_id={data['id']}")
    print(".env обновлён (токен + user_id).")


if __name__ == "__main__":
    main()

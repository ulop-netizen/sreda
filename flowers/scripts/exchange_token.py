"""Обмен короткоживущего токена на долгоживущий (60 дней) и его продление.

Использование:
    python scripts/exchange_token.py exchange <short_lived_token>
    python scripts/exchange_token.py refresh  <long_lived_token>

APP_SECRET берётся из .env (THREADS_APP_SECRET).
"""
import sys

import requests

from src import config

BASE = "https://graph.threads.net"


def exchange(short_token: str) -> None:
    resp = requests.get(
        f"{BASE}/access_token",
        params={
            "grant_type": "th_exchange_token",
            "client_secret": config.THREADS_APP_SECRET,
            "access_token": short_token,
        },
        timeout=30,
    )
    print(resp.status_code, resp.json())


def refresh(long_token: str) -> None:
    resp = requests.get(
        f"{BASE}/refresh_access_token",
        params={
            "grant_type": "th_refresh_token",
            "access_token": long_token,
        },
        timeout=30,
    )
    print(resp.status_code, resp.json())


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("exchange", "refresh"):
        print(__doc__)
        raise SystemExit(1)
    (exchange if sys.argv[1] == "exchange" else refresh)(sys.argv[2])

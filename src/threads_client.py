"""Тонкая обёртка над Threads Graph API: создать пост -> опубликовать."""
from __future__ import annotations

import time

import requests

BASE = "https://graph.threads.net/v1.0"
TEXT_LIMIT = 500


class ThreadsError(RuntimeError):
    pass


class ThreadsClient:
    def __init__(self, user_id: str, access_token: str, publish_delay: int = 5):
        self.user_id = user_id
        self.token = access_token
        self.publish_delay = publish_delay

    def _post(self, path: str, params: dict) -> dict:
        params = {**params, "access_token": self.token}
        resp = requests.post(f"{BASE}/{path}", params=params, timeout=60)
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400 or "error" in data:
            raise ThreadsError(f"{resp.status_code}: {data}")
        return data

    def _create_container(self, params: dict) -> str:
        return self._post(f"{self.user_id}/threads", params)["id"]

    def publish(self, creation_id: str) -> str:
        if self.publish_delay:
            time.sleep(self.publish_delay)
        return self._post(f"{self.user_id}/threads_publish", {"creation_id": creation_id})["id"]

    def post(self, text: str, image_url: str | None = None) -> str:
        """Полный цикл: вернёт id опубликованного поста."""
        if len(text) > TEXT_LIMIT:
            raise ThreadsError(f"Текст {len(text)} символов, лимит Threads — {TEXT_LIMIT}")
        if image_url:
            creation_id = self._create_container(
                {"media_type": "IMAGE", "image_url": image_url, "text": text}
            )
        else:
            creation_id = self._create_container({"media_type": "TEXT", "text": text})
        return self.publish(creation_id)

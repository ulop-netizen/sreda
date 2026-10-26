"""Тонкая обёртка над Threads Graph API: создать пост -> опубликовать."""
from __future__ import annotations

import time

import requests

BASE = "https://graph.threads.net/v1.0"
TEXT_LIMIT = 500
CAROUSEL_MAX = 20


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

    def post(self, text: str, image_url: str | None = None,
             image_urls: list[str] | None = None) -> str:
        """Полный цикл: вернёт id опубликованного поста.

        image_urls с 2+ картинками -> карусель (media_type=CAROUSEL).
        """
        if len(text) > TEXT_LIMIT:
            raise ThreadsError(f"Текст {len(text)} символов, лимит Threads — {TEXT_LIMIT}")
        urls = [u for u in (image_urls or []) if u]
        if len(urls) >= 2:
            return self.post_carousel(text, urls)
        if urls and not image_url:
            image_url = urls[0]
        if image_url:
            creation_id = self._create_container(
                {"media_type": "IMAGE", "image_url": image_url, "text": text}
            )
        else:
            creation_id = self._create_container({"media_type": "TEXT", "text": text})
        return self.publish(creation_id)

    def post_carousel(self, text: str, image_urls: list[str]) -> str:
        """Карусель: 2–20 картинок -> item-контейнеры -> CAROUSEL -> publish."""
        if not 2 <= len(image_urls) <= CAROUSEL_MAX:
            raise ThreadsError(f"Карусель: нужно 2–{CAROUSEL_MAX} картинок, дано {len(image_urls)}")
        children = [
            self._create_container(
                {"media_type": "IMAGE", "image_url": url, "is_carousel_item": "true"}
            )
            for url in image_urls
        ]
        if self.publish_delay:
            time.sleep(self.publish_delay)  # дать item-контейнерам обработаться
        creation_id = self._create_container(
            {"media_type": "CAROUSEL", "children": ",".join(children), "text": text}
        )
        return self.publish(creation_id)

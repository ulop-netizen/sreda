"""Точка входа: выбрать пост и опубликовать в Threads (или сухой прогон)."""
from __future__ import annotations

from . import config
from .content import append_log, pick_next
from .threads_client import ThreadsClient


def main() -> None:
    post = pick_next()
    text = post["caption"]
    img = config.image_url(post["image"]) if post["image"] else ""

    print(f"--- POST: {post['id']} ---")
    print(text)
    print(f"--- {len(text)} символов | картинка: {img or 'нет'} ---")

    if config.DRY_RUN:
        print("DRY_RUN=true — публикация пропущена.")
        return

    config.require_credentials()
    client = ThreadsClient(
        config.THREADS_USER_ID,
        config.THREADS_ACCESS_TOKEN,
        publish_delay=config.PUBLISH_DELAY_SECONDS,
    )
    post_id = client.post(text, image_url=img or None)
    print(f"Опубликовано. post_id={post_id}")
    append_log(post, post_id=post_id, dry_run=False)


if __name__ == "__main__":
    main()

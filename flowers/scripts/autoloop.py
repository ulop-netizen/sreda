"""Публикует очередь постов по одному с паузой. Останавливается, когда новые кончились.

    python -m scripts.autoloop [--interval SECONDS] [--max N]
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

from src import config
from src.content import _fingerprint, append_log, load_log, pick_next
from src.threads_client import ThreadsClient


def _arg(flag: str, default: int) -> int:
    return int(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def _now() -> str:
    return f"{datetime.now(timezone.utc):%H:%M}"


def main() -> None:
    interval = _arg("--interval", 1800)
    hard_max = _arg("--max", 40)
    alternate = "--alternate" in sys.argv  # чередовать image / text

    config.require_credentials()
    client = ThreadsClient(
        config.THREADS_USER_ID,
        config.THREADS_ACCESS_TOKEN,
        publish_delay=config.PUBLISH_DELAY_SECONDS,
    )

    kinds = ["image", "text"] if alternate else [None]
    published = 0
    for i in range(1, hard_max + 1):
        kind = kinds[(i - 1) % len(kinds)]
        post = pick_next(kind)
        already = {e["fp"] for e in load_log() if not e.get("dry_run")}
        if post is None or _fingerprint(post["caption"]) in already:
            other_left = any(
                pick_next(k) and _fingerprint(pick_next(k)["caption"]) not in already
                for k in kinds
                if k != kind
            )
            if not other_left:
                print(f"[{_now()}] всё опубликовано, стоп ({published} шт).")
                return
            print(f"[{_now()}] {kind}: пусто, пропускаю такт.")
            time.sleep(interval)
            continue

        img = config.image_url(post["image"]) if post["image"] else ""
        try:
            post_id = client.post(post["caption"], image_url=img or None)
            append_log(post, post_id=post_id, dry_run=False)
            published += 1
            print(f"[{_now()}] #{i} OK [{kind}] {post['id']} post_id={post_id}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{_now()}] #{i} ОШИБКА [{kind}] {post['id']}: {exc}")

        time.sleep(interval)

    print(f"достигнут лимит --max, стоп ({published} шт).")


if __name__ == "__main__":
    main()

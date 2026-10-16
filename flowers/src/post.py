"""Точка входа: выбрать пост и опубликовать в Threads (или сухой прогон).

    python -m src.post                    — следующий по очереди
    python -m src.post --only ID          — конкретный пост из posts.yaml
    python -m src.post --only ID --force  — то же, в обход защиты от частых постов

Guard: a real post is NOT published if the last logged real post was less than
MIN_GAP_HOURS ago (default 1.5, env MIN_GAP_HOURS). This stops late GitHub cron
runs from bunching posts together. Only `--force` (meant for manual --only runs)
bypasses it. A skipped run exits 0 so the Actions job stays green.

SLOT_MODE=1 (set by the scheduled workflow) also skips when today's real
posts already cover every Warsaw slot that has come due (08:10 / 11:10 /
18:10). `--force` bypasses that check too.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import config
from .content import append_log, last_posted_at, load_log, load_posts, pick_next
from .threads_client import ThreadsClient


def min_gap() -> timedelta:
    return timedelta(hours=float(os.getenv("MIN_GAP_HOURS", "1.5")))


def too_soon(now: datetime | None = None) -> tuple[bool, str]:
    """(True, reason) if the last real post is younger than the minimum gap."""
    last = last_posted_at()
    if last is None:
        return False, ""
    now = now or datetime.now(timezone.utc)
    age = now - last
    if age < min_gap():
        mins = int(age.total_seconds() // 60)
        return True, (
            f"GUARD: последний пост был {mins} мин назад ({last.isoformat()}), "
            f"минимум {min_gap()} — пропускаю. Для ручного поста: --only ID --force"
        )
    return False, ""


SLOTS = [(8, 10), (11, 10), (18, 10)]  # Warsaw local


def slot_missing(now=None):
    """(True, reason) if all slots due so far already have a real post today (Warsaw)."""
    tz = ZoneInfo("Europe/Warsaw")
    now = (now or datetime.now(timezone.utc)).astimezone(tz)
    due = sum(1 for h, m in SLOTS if (now.hour, now.minute) >= (h, m))
    done = sum(1 for e in load_log()
               if not e.get("dry_run") and e.get("at")
               and datetime.fromisoformat(e["at"].replace("Z", "+00:00")).astimezone(tz).date() == now.date())
    if done >= due:
        return True, f"SLOT: сегодня уже {done} пост(ов), слотов наступило {due} — пропускаю."
    return False, ""


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    force = "--force" in argv
    if "--only" in argv:
        wanted = argv[argv.index("--only") + 1]
        post = next((p for p in load_posts() if p["id"] == wanted), None)
        if post is None:
            raise SystemExit(f"Пост с id={wanted} не найден в posts.yaml (или parked)")
    else:
        post = pick_next()
        if post is None:
            raise SystemExit("Нет постов для публикации.")
    text = post["caption"]
    img = config.image_url(post["image"]) if post["image"] else ""

    print(f"--- POST: {post['id']} ---")
    print(text)
    print(f"--- {len(text)} символов | картинка: {img or 'нет'} ---")

    blocked, why = too_soon()
    if blocked and not force:
        print(why)
        return
    if blocked and force:
        print("GUARD bypassed with --force.")

    if os.getenv("SLOT_MODE") == "1" and not force:
        full, why = slot_missing()
        if full:
            print(why); return

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

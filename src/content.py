"""Выбор следующего поста из пула с ротацией (least-recently-used) + расчёт цены."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS_FILE = ROOT / "content" / "posts.yaml"
LOG_FILE = ROOT / "content" / "posted_log.json"


def _fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _price(base_pln, multiplier: float) -> str:
    if base_pln in (None, "", 0):
        return ""
    value = float(base_pln) * float(multiplier)
    rounded = max(9, round(value / 10) * 10 - 1)  # к ближайшему ...9
    return f"{rounded} zł"


def load_posts() -> list[dict]:
    raw = yaml.safe_load(POSTS_FILE.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults") or {}
    template = defaults.get("template", "{name}\n{price}")
    multiplier = defaults.get("price_multiplier", 1)

    out = []
    for item in raw.get("posts") or []:
        subs = {
            "name": str(item.get("name", "")).strip(),
            "price": _price(item.get("base_pln"), item.get("price_multiplier", multiplier)),
            "cta": str(defaults.get("cta", "")).strip(),
            "delivery": str(defaults.get("delivery", "")).strip(),
        }
        caption = str(item.get("caption") or template)
        for key, value in subs.items():
            caption = caption.replace("{" + key + "}", value)
        caption = "\n".join(line.rstrip() for line in caption.splitlines()).strip()
        if not caption:
            continue
        out.append(
            {
                "id": str(item.get("id") or _fingerprint(caption)),
                "image": str(item.get("image") or "").strip(),
                "caption": caption,
            }
        )
    if not out:
        raise SystemExit(f"В {POSTS_FILE} нет ни одного поста.")
    return out


def load_log() -> list[dict]:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    return []


def append_log(post: dict, post_id: str | None, dry_run: bool) -> None:
    log = load_log()
    log.append(
        {
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "id": post["id"],
            "fp": _fingerprint(post["caption"]),
            "image": post["image"],
            "post_id": post_id,
            "dry_run": dry_run,
            "preview": post["caption"].splitlines()[0][:80],
        }
    )
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_next() -> dict:
    """Пост, который дольше всех не публиковался (сухие прогоны не в счёт)."""
    posts = load_posts()
    last_seen: dict[str, str] = {}
    for entry in load_log():
        if entry.get("dry_run"):
            continue
        last_seen[entry["fp"]] = entry["at"]

    posts.sort(key=lambda p: last_seen.get(_fingerprint(p["caption"]), ""))
    return posts[0]

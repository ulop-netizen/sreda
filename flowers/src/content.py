"""Выбор следующего поста из пула с ротацией (least-recently-used) + расчёт цены."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS_FILE = ROOT / "content" / "posts.yaml"
# Extra batch files (e.g. posts-1026.yaml) are merged after posts.yaml.
EXTRA_POSTS_GLOB = "posts-*.yaml"
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
    out = []
    files = [POSTS_FILE] + sorted((ROOT / "content").glob(EXTRA_POSTS_GLOB))
    for f in files:
        out.extend(_load_file(f))
    if not out:
        raise SystemExit(f"В {POSTS_FILE} нет ни одного поста.")
    return out


def _load_file(path: Path) -> list[dict]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults") or {}
    template = defaults.get("template", "{name}\n{price}")
    multiplier = defaults.get("price_multiplier", 1)
    default_priority = int(defaults.get("priority", 0))

    out = []
    for item in raw.get("posts") or []:
        if item.get("parked"):
            continue  # parked: kept in the file, never posted
        explicit = item.get("price_pln")
        price = f"{explicit} zł" if explicit else _price(
            item.get("base_pln"), item.get("price_multiplier", multiplier)
        )
        subs = {
            "name": str(item.get("name", "")).strip(),
            "price": price,
            # Captions are single-language RU or PL (no English). Empty when no price —
            # the line is dropped from the template. Never invent prices.
            "price_line": f"{price}" if price else "",
            "cta": str(defaults.get("cta", "")).strip(),
            "delivery": str(defaults.get("delivery", "")).strip(),
        }
        caption = str(item.get("caption") or template)
        if not price:
            caption = "\n".join(
                line
                for line in caption.splitlines()
                if "{price}" not in line and "{price_line}" not in line
            )
        # Dłuższe klucze pierwsze, żeby {price} nie zjadło {price_line}.
        for key, value in sorted(subs.items(), key=lambda kv: -len(kv[0])):
            caption = caption.replace("{" + key + "}", value)
        caption = "\n".join(line.rstrip() for line in caption.splitlines()).strip()
        if not caption:
            continue
        out.append(
            {
                "id": str(item.get("id") or _fingerprint(caption)),
                "image": str(item.get("image") or "").strip(),
                # images: 2+ files -> carousel; image stays the first one for logs/filters
                "images": [str(x).strip() for x in (item.get("images") or []) if str(x).strip()],
                "priority": int(item.get("priority", default_priority)),
                "caption": caption,
            }
        )
        if out[-1]["images"] and not out[-1]["image"]:
            out[-1]["image"] = out[-1]["images"][0]
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


def last_posted_at() -> datetime | None:
    """Time of the most recent real (non-dry-run) post in the log, or None."""
    times = [
        datetime.fromisoformat(e["at"].replace("Z", "+00:00"))
        for e in load_log()
        if not e.get("dry_run") and e.get("at")
    ]
    return max(times) if times else None


def pick_next(kind: str | None = None) -> dict | None:
    """Пост, который дольше всех не публиковался (сухие прогоны не в счёт).

    kind="image" — только с картинкой; kind="text" — только текстовые;
    None — любой. Возвращает None, если подходящих нет.
    """
    posts = load_posts()
    if kind == "image":
        posts = [p for p in posts if p["image"]]
    elif kind == "text":
        posts = [p for p in posts if not p["image"]]
    if not posts:
        return None

    # Dedupe by caption fingerprint AND by id, so fixing the text of an
    # already-published entry (same id) does not make it "new" again.
    last_seen: dict[str, str] = {}
    for entry in load_log():
        if entry.get("dry_run"):
            continue
        last_seen["fp:" + entry["fp"]] = entry["at"]
        if entry.get("id"):
            last_seen["id:" + entry["id"]] = entry["at"]

    def _seen(p: dict) -> str:
        return max(
            last_seen.get("fp:" + _fingerprint(p["caption"]), ""),
            last_seen.get("id:" + p["id"], ""),
        )

    # LRU first; among equally-unseen posts, higher priority (new batches) first.
    posts.sort(key=lambda p: (_seen(p), -p.get("priority", 0)))
    return posts[0]

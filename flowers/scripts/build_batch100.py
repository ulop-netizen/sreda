#!/usr/bin/env python3
"""(HISTORICAL — already run; superseded by warsaw_fix.py.)
Build ~100 metadata-stripped image variants + append posts.yaml entries.

Source: only flowers/images/*.jpg (not batch-100/, not thumbs).
Captions: one language per post (EN or RU), #Warszawa hashtags, no prices.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "images"
OUT_DIR = SRC_DIR / "batch-100"
YAML_PATH = ROOT / "content" / "posts.yaml"
N = 100

EN_CAPTIONS = [
    "Soft petals, bold mood — a bouquet made to linger.\nAvailable to order in #Warszawa 📍\nDM to order or customize your own!",
    "Colour therapy in a vase. Fresh, seasonal, made for you.\nShip or pickup in #Warszawa\nMessage me in DM to book.",
    "When words are not enough — send flowers that speak louder.\nCustom arrangements for #Warszawa\nDM to order.",
    "A quiet luxury: hand-tied blooms with character.\nOrder for delivery across #Warszawa 🌸\nWrite in DM.",
    "Bright stems for grey days. Studio favourites, ready on request.\n#Warszawa flower studio\nDM for yours.",
    "Texture, tone, and a little drama — our kind of bouquet.\nAvailable in #Warszawa\nDM to reserve.",
    "Not supermarket flowers. Thoughtful composition, seasonal picks.\nServing #Warszawa\nDM to order.",
    "Make an ordinary Tuesday feel special.\nBouquets on order — #Warszawa 📍\nMessage me in DM.",
    "Soft blush tones for someone who deserves softness.\nCustom work for #Warszawa\nDM to start.",
    "Deep colour, clean lines — florals with presence.\n#Warszawa · made to order\nDM for details.",
    "A pocket of summer, tied by hand.\nDelivery & pickup in #Warszawa\nWrite in DM.",
    "Statement blooms for a dinner table that means it.\n#Warszawa floral studio\nDM to order.",
    "Peony energy even when peonies are scarce — we find the mood.\nOrders in #Warszawa\nDM me.",
    "Gentle chaos of petals. Perfect for an unexpected gift.\n#Warszawa\nDM to book.",
    "Rich burgundy and warm accents — autumn in a vase.\nAvailable across #Warszawa 🍂\nDM to order.",
    "Fresh cut, carefully packed, delivered with care.\nFlower orders for #Warszawa\nMessage in DM.",
    "Small bouquet, big feeling.\nCustom sizes for #Warszawa clients\nDM to choose.",
    "Hydrangea drama and supporting cast — full and lush.\n#Warszawa studio\nDM for yours.",
    "Orange fire meets soft green — a joyful clash.\nOn request in #Warszawa\nWrite in DM.",
    "Classic romance, modern edit.\nBouquets for #Warszawa 💐\nDM to order or tweak.",
    "For birthdays, apologies, or just because.\nServing #Warszawa\nDM anytime.",
    "Clean whites and soft creams — calm on a table.\n#Warszawa floral design\nDM to reserve.",
    "Wild-looking, carefully built. That is the point.\nOrders in #Warszawa\nMessage me.",
    "A gift that arrives looking expensive — because it is considered.\n#Warszawa delivery available\nDM to book.",
    "Seasonal palette, no filler fluff.\nHand-tied in #Warszawa\nDM for a quote (no prices in posts).",
    "Bring the garden indoors for one beautiful week.\n#Warszawa\nDM to order.",
    "Bold anthurium energy for modern interiors.\nAvailable to order in #Warszawa\nWrite in DM.",
    "Dahlias that refuse to be boring.\nCustom bouquets — #Warszawa 📍\nDM me.",
    "Soft morning light vibes, any time of day.\n#Warszawa flower studio\nDM to start your order.",
    "Wrapped with care, ready to surprise someone in #Warszawa.\nMessage in DM to arrange.",
    "Minimal vase, maximal colour.\nStudio pieces for #Warszawa homes\nDM to order.",
    "If you want “wow” without trying too hard — this is it.\n#Warszawa\nDM for yours.",
    "Layered greens and a single bright accent.\nMade to order in #Warszawa\nWrite in DM.",
    "Celebrate quietly. Flowers do the talking.\n#Warszawa floral studio\nDM to book.",
    "A bouquet that photographs as well as it looks in person.\nOrders for #Warszawa\nDM me.",
    "Warm tones for cooler evenings.\nSeasonal work — #Warszawa 🍂\nMessage in DM.",
    "Petals with personality — not a generic mix.\n#Warszawa · custom only\nDM to design together.",
    "Same flowers, different story each time — ask for your version.\nServing #Warszawa\nDM to order.",
    "Elegant enough for a hotel lobby, personal enough for home.\n#Warszawa\nDM for delivery.",
    "Treat yourself. Seriously.\nBouquets on request in #Warszawa 🌸\nWrite in DM.",
    "Coral, cream, and a little sparkle of green.\nAvailable in #Warszawa\nDM to reserve.",
    "When the table needs a centrepiece, not decoration.\n#Warszawa studio\nDM to order.",
    "Fresh stems, honest composition, no plastic shine.\nFlower orders — #Warszawa\nMessage me.",
    "A thank-you that feels like a thank-you.\nCustom gifts for #Warszawa\nDM anytime.",
    "Moody florals for people who skip pastels.\n#Warszawa made-to-order\nDM for dark & rich.",
    "Light, airy, and impossible to ignore.\nPickup or delivery in #Warszawa\nDM to book.",
    "Built stem by stem — nothing random.\n#Warszawa floral design\nWrite in DM.",
    "Send colour to someone across the city.\n#Warszawa\nDM to arrange.",
    "Studio drop: another favourite composition, ready when you are.\nOrders in #Warszawa\nDM me.",
    "Flowers that hold their shape through the week — with proper care tips on request.\n#Warszawa\nDM to order.",
]

RU_CAPTIONS = [
    "Мягкие лепестки и смелый характер — букет, который хочется рассматривать.\nНа заказ в #Warszawa 📍\nНапишите в DM — соберём ваш вариант.",
    "Цветотерапия в вазе. Свежие сезонные стебли под ваш запрос.\n#Warszawa\nПишите в директ.",
    "Когда слов мало — пусть скажут цветы.\nДоставка и самовывоз в #Warszawa\nDM для заказа.",
    "Тихая роскошь: ручная сборка и живой характер.\nСтудия цветов #Warszawa 🌸\nНапишите в DM.",
    "Яркие стебли для серых дней. Любимые композиции студии.\nЗаказы по #Warszawa\nПишите в директ.",
    "Фактура, тон и чуть драмы — наш любимый рецепт.\nДоступно в #Warszawa\nDM, чтобы забронировать.",
    "Не «как из супермаркета». Продуманная композиция и сезон.\n#Warszawa\nНапишите в DM.",
    "Пусть обычный вторник станет чуть особеннее.\nБукеты на заказ — #Warszawa 📍\nПишите в директ.",
    "Нежный румянец для тех, кому нужна мягкость.\nИндивидуальные заказы в #Warszawa\nDM, чтобы начать.",
    "Глубокий цвет и чистые линии — цветы с присутствием.\n#Warszawa · под заказ\nНапишите в DM.",
    "Карман лета, связанный вручную.\nДоставка и самовывоз в #Warszawa\nПишите в директ.",
    "Акцент на стол, который задаёт настроение ужина.\nЦветочная студия #Warszawa\nDM для заказа.",
    "Энергия пионов даже когда пионов мало — мы ловим настроение.\nЗаказы в #Warszawa\nПишите в DM.",
    "Лёгкий хаос лепестков. Идеально для неожиданного подарка.\n#Warszawa\nНапишите в директ.",
    "Бордо и тёплые акценты — осень в вазе.\nПо всему #Warszawa 🍂\nDM для заказа.",
    "Свежий срез, аккуратная упаковка, бережная доставка.\nЦветы для #Warszawa\nПишите в директ.",
    "Маленький букет — большое чувство.\nРазные размеры для клиентов #Warszawa\nDM, чтобы выбрать.",
    "Драма гортензии и поддерживающий «хор» стеблей.\nСтудия #Warszawa\nНапишите в DM.",
    "Оранжевый огонь и мягкая зелень — радостный контраст.\nПод заказ в #Warszawa\nПишите в директ.",
    "Классическая романтика в современном прочтении.\nБукеты для #Warszawa 💐\nDM — закажем или подправим.",
    "На день рождения, «прости» или просто так.\n#Warszawa\nПишите в любое время.",
    "Чистые белые и кремовые тона — спокойствие на столе.\nФлористика #Warszawa\nDM, чтобы забронировать.",
    "Выглядит «дико», собрано очень осознанно. В этом и смысл.\nЗаказы в #Warszawa\nНапишите в директ.",
    "Подарок, который выглядит дорого — потому что продуман.\nДоставка по #Warszawa\nDM для брони.",
    "Сезонная палитра, без пустого наполнителя.\nСборка вручную в #Warszawa\nПишите в DM.",
    "Принесите сад в дом хотя бы на неделю.\n#Warszawa\nНапишите в директ для заказа.",
    "Смелая энергия антуриума для современных интерьеров.\nНа заказ в #Warszawa\nПишите в DM.",
    "Георгины, которые отказываются быть скучными.\nАвторские букеты — #Warszawa 📍\nDM мне.",
    "Настроение мягкого утра — в любое время дня.\nЦветочная студия #Warszawa\nНапишите, чтобы начать заказ.",
    "Упаковано с заботой — готово удивить кого-то в #Warszawa.\nПишите в DM, чтобы договориться.",
    "Минимальная ваза — максимум цвета.\nСтудийные работы для домов #Warszawa\nDM для заказа.",
    "Если нужно «вау» без лишних усилий — вот оно.\n#Warszawa\nНапишите в директ.",
    "Слои зелени и один яркий акцент.\nПод заказ в #Warszawa\nПишите в DM.",
    "Отметьте тихо. Цветы скажут за вас.\nСтудия #Warszawa\nDM для брони.",
    "Букет, который хорошо смотрится и вживую, и на фото.\nЗаказы для #Warszawa\nНапишите мне.",
    "Тёплые тона для прохладных вечеров.\nСезонные работы — #Warszawa 🍂\nПишите в директ.",
    "Лепестки с характером — не случайный микс.\n#Warszawa · только под заказ\nDM, соберём вместе.",
    "Те же цветы — другая история. Попросите свою версию.\nОбслуживаем #Warszawa\nНапишите в DM.",
    "Достаточно элегантно для лобби и достаточно лично для дома.\n#Warszawa\nDM по доставке.",
    "Подарите себе. Серьёзно.\nБукеты по запросу в #Warszawa 🌸\nПишите в директ.",
    "Коралл, крем и искорка зелени.\nДоступно в #Warszawa\nDM, чтобы зарезервировать.",
    "Когда столу нужен центр, а не «просто украшение».\nСтудия #Warszawa\nНапишите для заказа.",
    "Свежие стебли, честная композиция, без пластикового блеска.\nЦветы — #Warszawa\nПишите в DM.",
    "«Спасибо», которое ощущается как спасибо.\nПодарки для #Warszawa\nDM в любое время.",
    "Мрачные, насыщенные тона — для тех, кто минует пастель.\n#Warszawa под заказ\nПишите за тёмным и богатым.",
    "Лёгкий, воздушный и невозможно не заметить.\nСамовывоз или доставка в #Warszawa\nDM для брони.",
    "Стебель за стеблем — ничего случайного.\nФлористика #Warszawa\nНапишите в директ.",
    "Отправьте цвет кому-то через весь город.\n#Warszawa\nDM, чтобы организовать.",
    "Ещё одна любимая сборка студии — готова, когда вы готовы.\nЗаказы в #Warszawa\nПишите мне.",
    "Цветы, которые держат форму неделю — с советами по уходу по запросу.\n#Warszawa\nDM для заказа.",
]

assert len(EN_CAPTIONS) == 50 and len(RU_CAPTIONS) == 50


def source_images() -> list[Path]:
    files = sorted(
        p
        for p in SRC_DIR.glob("*.jpg")
        if p.is_file() and p.parent == SRC_DIR
    )
    if not files:
        raise SystemExit(f"No source jpgs in {SRC_DIR}")
    return files


def variant(img: Image.Image, seed: int) -> Image.Image:
    """Light unique-ish transform; always RGB JPEG without EXIF."""
    rng = random.Random(seed)
    w, h = img.size
    # subtle crop 0–4% each side
    left = int(w * rng.uniform(0, 0.04))
    top = int(h * rng.uniform(0, 0.04))
    right = w - int(w * rng.uniform(0, 0.04))
    bottom = h - int(h * rng.uniform(0, 0.04))
    if right - left < w * 0.85:
        left, right = 0, w
    if bottom - top < h * 0.85:
        top, bottom = 0, h
    cropped = img.crop((left, top, right, bottom))
    # occasional slight rotate (expand then center-crop back)
    angle = rng.choice([0, 0, 0, -1.5, 1.5, -2.0, 2.0])
    if angle:
        rotated = cropped.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(255, 255, 255))
        # center crop to original cropped size-ish
        rw, rh = rotated.size
        cw, ch = cropped.size
        if rw >= cw and rh >= ch:
            x0 = (rw - cw) // 2
            y0 = (rh - ch) // 2
            cropped = rotated.crop((x0, y0, x0 + cw, y0 + ch))
        else:
            cropped = rotated
    if cropped.mode != "RGB":
        cropped = cropped.convert("RGB")
    return cropped


def build_images(sources: list[Path]) -> list[str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for i in range(1, N + 1):
        src = sources[(i - 1) % len(sources)]
        with Image.open(src) as im:
            out = variant(im, seed=1000 + i)
            # normalize long edge ~1600 max for Threads-friendly size
            max_edge = 1600
            w, h = out.size
            scale = min(1.0, max_edge / max(w, h))
            if scale < 1.0:
                out = out.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            name = f"batch-{i:03d}.jpg"
            path = OUT_DIR / name
            quality = 88 + (i % 5)  # 88–92 slight re-encode variance
            # save WITHOUT exif / icc
            out.save(path, format="JPEG", quality=quality, optimize=True, exif=b"")
        names.append(f"batch-100/{name}")
        if i % 20 == 0:
            print(f"  images {i}/{N}")
    return names


def yaml_block(post_id: str, image: str, lang: str, caption: str) -> str:
    # indent caption lines for YAML literal block
    cap_lines = "\n".join("      " + line if line else "      " for line in caption.splitlines())
    first = caption.splitlines()[0][:90]
    return (
        f"\n  - id: {post_id}\n"
        f"    image: {image}\n"
        f"    name: {first!r}\n"
        f"    lang: {lang}\n"
        f"    caption: |\n"
        f"{cap_lines}\n"
    )


def append_yaml(image_paths: list[str]) -> None:
    text = YAML_PATH.read_text(encoding="utf-8")
    if "batch-001" in text or "id: batch-001" in text:
        raise SystemExit("posts.yaml already contains batch entries — abort to avoid dupes")

    # Update header comment + defaults for NEW template-based posts
    # Keep old posts intact; change defaults so future non-caption posts follow Warsaw/one-lang intent.
    new_defaults = """# Pool for @july.concept.flowers.
# New batch posts: ONE language per caption (EN or RU), #Warszawa hashtags, no prices.
# Do not rewrite already-published captions.
#
# Entry: id / image (file under images/) / name / optional caption / optional price_pln
# Text-only = id + caption, no image.

defaults:
  price_multiplier: 1.8
  cta: "DM to order or customize your own!"
  template: |
    {name}
    {price_line}
    Available to order in #Warszawa 📍
    {cta}

posts:"""

    # Replace from start through "posts:" first occurrence carefully
    marker = "\nposts:\n"
    if marker not in text and not text.lstrip().startswith("posts:"):
        # try windows-ish
        idx = text.find("posts:")
        if idx < 0:
            raise SystemExit("posts: key not found")
    # Rebuild: new header/defaults + everything after first "posts:" line's content
    posts_idx = text.find("\nposts:")
    if posts_idx < 0:
        raise SystemExit("cannot find posts: section")
    # keep existing posts body (after "posts:\n")
    body_start = text.find("\n", posts_idx + 1) + 1
    existing_posts = text[body_start:]

    blocks = []
    for i in range(1, N + 1):
        lang = "en" if i % 2 == 1 else "ru"
        cap = EN_CAPTIONS[(i - 1) // 2] if lang == "en" else RU_CAPTIONS[(i - 1) // 2]
        # for i=1 en idx0, i=2 ru idx0, i=3 en idx1, i=4 ru idx1 ...
        blocks.append(yaml_block(f"batch-{i:03d}", image_paths[i - 1], lang, cap))

    new_text = new_defaults + "\n" + existing_posts.rstrip() + "\n\n  # ---------- BATCH-100 (EN/RU single-lang, #Warszawa) ----------\n" + "".join(blocks)
    if not new_text.endswith("\n"):
        new_text += "\n"
    YAML_PATH.write_text(new_text, encoding="utf-8")
    print(f"appended {N} yaml entries")


def main() -> None:
    sources = source_images()
    print(f"sources: {len(sources)}")
    for s in sources:
        print(f"  - {s.name}")
    paths = build_images(sources)
    append_yaml(paths)
    # verify no exif on a sample
    sample = OUT_DIR / "batch-001.jpg"
    with Image.open(sample) as im:
        exif = im.getexif()
        print(f"sample {sample.name} size={im.size} exif_items={len(exif)}")
    print("done")


if __name__ == "__main__":
    main()

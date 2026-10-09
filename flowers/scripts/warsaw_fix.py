#!/usr/bin/env python3
"""One-off: location -> Warsaw, descriptive names, +50 new clean photo variants.

- Rewrites everything from `sasha-17` onwards in content/posts.yaml.
- Already-posted entries keep their id (content.py dedupes by id as well as caption fp).
- Unposted batch entries get descriptive ids/names, single-language captions, #Warszawa.
- Generates images/batch-50/var-001..050.jpg (EXIF/ICC stripped) + 50 queue entries.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
YAML_PATH = ROOT / "content" / "posts.yaml"
LOG_PATH = ROOT / "content" / "posted_log.json"
OUT50 = IMG / "batch-50"

# Celebrity stock photo — not a studio bouquet, never queued on its own. Skip.
EXCLUDE = {"hydrangea-pink.jpg"}

# source image -> (slug, EN name, RU name)
NAMES = {
    "autumn-pocket.jpg": ("autumn-pocket", "Pocket bouquet in autumn tones 🍂", "Карманный букет в осенних тонах 🍂"),
    "blush-anthurium.jpg": ("blush-hydrangea-anthurium", "Blush hydrangea & pink anthurium 🌸", "Нежная гортензия и розовый антуриум 🌸"),
    "calla-line.jpg": ("peach-callas", "Peach calla lilies, drawn out in a line ✨", "Персиковые каллы, выстроенные в линию ✨"),
    "crimson-drama.jpg": ("crimson-still-life", "Crimson still life — strawflower, anthurium, smokebush 🍷", "Багровый натюрморт — гелихризум, антуриум, скумпия 🍷"),
    "dahlia-ember.jpg": ("ember-dahlias", "Ember dahlias on burgundy hydrangea 🔥", "Огненные георгины на бордовой гортензии 🔥"),
    "green-cascade.jpg": ("chartreuse-cascade", "Chartreuse cascade — bells of Ireland & hanging amaranth 🌿", "Салатовый каскад — молюцелла и свисающий амарант 🌿"),
    "peonies-coral.jpg": ("coral-peonies", "Coral peonies — an oversized statement bouquet 🌷", "Коралловые пионы — большой эффектный букет 🌷"),
    "ranunculus-carnival.jpg": ("ranunculus-carnival", "Ranunculus carnival — orange, pink, yellow 🎪", "Карнавал ранункулюсов — оранжевый, розовый, жёлтый 🎪"),
    "ranunculus-vase.jpg": ("ranunculus-chamomile-vase", "Ranunculus & chamomile in a ceramic vase 🤍", "Ранункулюсы и ромашка в керамической вазе 🤍"),
    "roses-letters.jpg": ("red-rose-letters", "Red rose letter boxes — spell your word or date 🌹", "Буквы из красных роз — ваше слово или дата 🌹"),
    "sasha-01.jpg": ("blushing-peonies", "Blushing peonies — pink & cream ruffles 🌸", "Нежные пионы — розовые и кремовые оборки 🌸"),
    "sasha-02.jpg": ("anthurium-dahlia-physalis", "Red anthurium, burgundy dahlia & physalis 🍂", "Красный антуриум, бордовая георгина и физалис 🍂"),
    "sasha-03.jpg": ("burgundy-hydrangea-billy-balls", "Burgundy hydrangea with billy balls & dahlia 🟡", "Бордовая гортензия с краспедией и георгиной 🟡"),
    "sasha-04.jpg": ("burgundy-hydrangea-orange-dahlia", "Burgundy hydrangea, orange dahlia & green anthurium 🧡", "Бордовая гортензия, оранжевая георгина и зелёный антуриум 🧡"),
    "sasha-05.jpg": ("fiery-crocosmia", "Fiery crocosmia with glossy red berries 🔥", "Огненная крокосмия с блестящими красными ягодами 🔥"),
    "sasha-06.jpg": ("pink-hydrangea-anthurium", "Pink hydrangea, pink anthurium & bells of Ireland 🌿", "Розовая гортензия, розовый антуриум и ирландские колокольчики 🌿"),
    "sasha-07.jpg": ("peach-pompon-dahlias", "Peach & pink pompon dahlias 🍑", "Персиковые и розовые помпонные георгины 🍑"),
    "sasha-08.jpg": ("burgundy-hydrangea-stock", "Burgundy hydrangea, peach stock & white dahlias 🤍", "Бордовая гортензия, персиковая левкоя и белые георгины 🤍"),
    "sasha-09.jpg": ("deep-hydrangea-pompons", "Deep hydrangea, peach stock & white pompons ✨", "Глубокая гортензия, персиковая левкоя и белые помпоны ✨"),
    "sasha-10.jpg": ("carmine-and-smoke", "Carmine & smoke — red anthurium, dark daisy, ornamental allium 🍷", "Кармин и дым — красный антуриум, тёмная маргаритка, декоративный лук 🍷"),
    "sasha-11.jpg": ("flame-parrot-flowers", "Flame parrot flowers, orange berries & limonium 🧡", "Огненные попугайные цветы, оранжевые ягоды и лимониум 🧡"),
    "sasha-12.jpg": ("brunia-sea-lavender", "Brunia & sea lavender in a textured vase 🌿", "Бруния и морская лаванда в фактурной вазе 🌿"),
    "sasha-13.jpg": ("green-berries-statice", "Green berry clusters & lavender statice 💜", "Зелёные ягодные грозди и лавандовый статице 💜"),
    "sasha-14.jpg": ("golden-chrysanthemums", "Golden pompon chrysanthemums 💛", "Золотые помпонные хризантемы 💛"),
    "sasha-15.jpg": ("pink-rose-lilies", "Pink double rose lilies — pink & cream 🌷", "Нежно-розовые махровые розолилии 🌷"),
    "sasha-16.jpg": ("copper-chrysanthemums", "Sunny yellow & copper autumn chrysanthemums ☀️", "Солнечно-жёлтые и медные осенние хризантемы ☀️"),
    "sasha-17.jpg": ("dahlia-calla-gentian", "Orange dahlia, sunset calla & blue gentian 💙", "Оранжевая георгина, закатная калла и синяя горечавка 💙"),
    "sasha-18.jpg": ("gentian-yellow-dahlia", "Blue gentian, yellow dahlia & orange callas 🔵", "Синяя горечавка, жёлтая георгина и оранжевые каллы 🔵"),
    "sasha-19.jpg": ("sunset-callas-sapphire", "Sunset callas, orange dahlias & sapphire blue 🌅", "Закатные каллы, оранжевые георгины и сапфировый синий 🌅"),
    "sasha-20.jpg": ("gentian-pompon-dahlia", "Blue gentian, orange pompon dahlia & sunset calla ✨", "Синяя горечавка, оранжевая помпонная георгина и закатная калла ✨"),
    "soft-morning.jpg": ("soft-morning", "Soft morning — cream gerbera, spray roses, blue tweedia ☁️", "Нежное утро — кремовая гербера, кустовые розы, голубая твидия ☁️"),
}

EN_MOOD = [
    "Soft petals, bold mood — a bouquet made to linger.",
    "Colour therapy in a vase. Fresh, seasonal, made for you.",
    "When words are not enough — send flowers that speak louder.",
    "A quiet luxury: hand-tied blooms with character.",
    "Bright stems for grey days. Studio favourites, ready on request.",
    "Texture, tone, and a little drama — our kind of bouquet.",
    "Not supermarket flowers. Thoughtful composition, seasonal picks.",
    "Make an ordinary Tuesday feel special.",
    "Soft tones for someone who deserves softness.",
    "Deep colour, clean lines — florals with presence.",
    "A pocket of summer, tied by hand.",
    "Statement blooms for a dinner table that means it.",
    "A bouquet that sets the mood before anyone says a word.",
    "Gentle chaos of petals. Perfect for an unexpected gift.",
    "Rich colour and warm accents — the season in a vase.",
    "Fresh cut, carefully packed, delivered with care.",
    "Small bouquet, big feeling.",
    "Full, lush and generous — nothing skimpy here.",
    "A joyful clash of colour that just works.",
    "Classic romance, modern edit.",
    "For birthdays, apologies, or just because.",
    "Calm colours that make a whole room breathe.",
    "Wild-looking, carefully built. That is the point.",
    "A gift that arrives looking expensive — because it is considered.",
    "Seasonal palette, no filler fluff.",
    "Bring the garden indoors for one beautiful week.",
    "Bold energy for modern interiors.",
    "Flowers that refuse to be boring.",
    "Soft morning light vibes, any time of day.",
    "Wrapped with care, ready to surprise someone you love.",
    "Minimal vase, maximal colour.",
    "If you want “wow” without trying too hard — this is it.",
    "Layered textures and one bright accent.",
    "Celebrate quietly. Flowers do the talking.",
    "A bouquet that photographs as well as it looks in person.",
    "Warm tones for cooler evenings.",
    "Petals with personality — not a generic mix.",
    "Same flowers, different story each time — ask for your version.",
    "Elegant enough for a hotel lobby, personal enough for home.",
    "Treat yourself. Seriously.",
    "A little sparkle for an ordinary day.",
    "When the table needs a centrepiece, not decoration.",
    "Fresh stems, honest composition, no plastic shine.",
    "A thank-you that feels like a thank-you.",
    "Moody florals for people who skip pastels.",
    "Light, airy, and impossible to ignore.",
    "Built stem by stem — nothing random.",
    "Send colour to someone across the city.",
    "Studio drop: another favourite composition, ready when you are.",
    "Flowers that hold their shape all week — care tips on request.",
]

RU_MOOD = [
    "Мягкие лепестки и смелый характер — букет, который хочется рассматривать.",
    "Цветотерапия в вазе. Свежие сезонные стебли под ваш запрос.",
    "Когда слов мало — пусть скажут цветы.",
    "Тихая роскошь: ручная сборка и живой характер.",
    "Яркие стебли для серых дней. Любимые композиции студии.",
    "Фактура, тон и чуть драмы — наш любимый рецепт.",
    "Не «как из супермаркета». Продуманная композиция и сезон.",
    "Пусть обычный вторник станет чуть особеннее.",
    "Нежные тона для тех, кому нужна мягкость.",
    "Глубокий цвет и чистые линии — цветы с характером.",
    "Кусочек лета, собранный вручную.",
    "Акцент на стол, который задаёт настроение ужина.",
    "Букет, который создаёт настроение раньше слов.",
    "Лёгкий хаос лепестков. Идеально для неожиданного подарка.",
    "Насыщенный цвет и тёплые акценты — сезон в вазе.",
    "Свежий срез, аккуратная упаковка, бережная доставка.",
    "Маленький букет — большое чувство.",
    "Пышно, щедро и объёмно — без экономии на цветах.",
    "Радостный контраст цвета, который просто работает.",
    "Классическая романтика в современном прочтении.",
    "На день рождения, «прости» или просто так.",
    "Спокойные цвета, с которыми дышит вся комната.",
    "Выглядит «дико», собрано очень осознанно. В этом и смысл.",
    "Подарок, который выглядит дорого — потому что продуман.",
    "Сезонная палитра, без пустого наполнителя.",
    "Принесите сад в дом хотя бы на неделю.",
    "Смелая энергия для современных интерьеров.",
    "Цветы, которые отказываются быть скучными.",
    "Настроение мягкого утра — в любое время дня.",
    "Упаковано с заботой — готово удивить того, кого вы любите.",
    "Минимальная ваза — максимум цвета.",
    "Если нужно «вау» без лишних усилий — вот оно.",
    "Слои фактур и один яркий акцент.",
    "Отметьте тихо. Цветы скажут за вас.",
    "Букет, который хорошо смотрится и вживую, и на фото.",
    "Тёплые тона для прохладных вечеров.",
    "Лепестки с характером — не случайный микс.",
    "Те же цветы — другая история. Попросите свою версию.",
    "Достаточно элегантно для лобби и достаточно лично для дома.",
    "Подарите себе. Серьёзно.",
    "Немного блеска для обычного дня.",
    "Когда столу нужен центр, а не «просто украшение».",
    "Свежие стебли, честная композиция, без пластикового блеска.",
    "«Спасибо», которое ощущается как спасибо.",
    "Глубокие, насыщенные тона — для тех, кто проходит мимо пастели.",
    "Лёгкий, воздушный и невозможно не заметить.",
    "Стебель за стеблем — ничего случайного.",
    "Отправьте цвет кому-то через весь город.",
    "Ещё одна любимая сборка студии — готова, когда вы готовы.",
    "Цветы, которые держат форму всю неделю — подскажу, как ухаживать.",
]
assert len(EN_MOOD) == 50 and len(RU_MOOD) == 50

EN_LOC = [
    "Available to order in Warsaw 📍 #Warszawa",
    "Delivery across Warsaw 🚗 #Warszawa",
    "Made to order in Warsaw #Warszawa",
    "Pickup or delivery in Warsaw 📍 #Warszawa",
]
EN_CTA = [
    "DM to order or customize your own!",
    "Message me in DM to book.",
    "Write in DM — I'll make your version.",
    "DM for details.",
]
RU_LOC = [
    "На заказ по Варшаве 📍 #Warszawa",
    "Доставка по Варшаве 🚗 #Warszawa",
    "Собираю под заказ в Варшаве #Warszawa",
    "Самовывоз или доставка по Варшаве 📍 #Warszawa",
]
RU_CTA = [
    "Напишите в DM — соберём ваш вариант.",
    "Пишите в директ для заказа.",
    "DM — подскажу по букету и срокам.",
    "Напишите в DM, чтобы заказать.",
]

HEADER = """# Pool for @july.concept.flowers — studio location: WARSAW only (#Warszawa).
# Batch posts: ONE language per caption (full EN or full RU), #Warszawa, no prices.
# Dedupe = caption fingerprint OR id (see src/content.py) — never change ids of
# already-published entries.
#
# Entry: id / image (file under images/) / name / optional caption / optional price_pln
# Text-only = id + caption, no image.

defaults:
  price_multiplier: 1.8
  cta: "DM to order or customize your own!"
  template: |
    {name}
    {price_line}
    Available to order in Warsaw 📍 #Warszawa
    {cta}

posts:
"""


def caption(lang: str, name: str, mood_i: int, k: int) -> str:
    if lang == "en":
        return "\n".join([name, EN_MOOD[mood_i % 50], EN_LOC[k % 4], EN_CTA[(k // 4 + k) % 4]])
    return "\n".join([name, RU_MOOD[mood_i % 50], RU_LOC[k % 4], RU_CTA[(k // 4 + k) % 4]])


def block(pid: str, image: str, name: str, lang: str, cap: str) -> str:
    lines = "\n".join("      " + ln for ln in cap.splitlines())
    return (
        f"  - id: {pid}\n    image: {image}\n    name: {json.dumps(name, ensure_ascii=False)}\n"
        f"    lang: {lang}\n    caption: |\n{lines}\n\n"
    )


def variant(src: Path, seed: int, out: Path) -> None:
    rng = random.Random(seed)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        w, h = im.size
        l, t = int(w * rng.uniform(0.01, 0.05)), int(h * rng.uniform(0.01, 0.05))
        r, b = w - int(w * rng.uniform(0.01, 0.05)), h - int(h * rng.uniform(0.01, 0.05))
        im = im.crop((l, t, r, b))
        ang = rng.choice([-2.5, -1.5, -1.0, 1.0, 1.5, 2.5])
        cw, ch = im.size
        rot = im.rotate(ang, resample=Image.Resampling.BICUBIC, expand=False)
        m = 0.05  # crop off rotated corners
        im = rot.crop((int(cw * m), int(ch * m), int(cw * (1 - m)), int(ch * (1 - m))))
        im = ImageEnhance.Brightness(im).enhance(rng.uniform(0.95, 1.06))
        im = ImageEnhance.Contrast(im).enhance(rng.uniform(0.95, 1.07))
        im = ImageEnhance.Color(im).enhance(rng.uniform(0.93, 1.10))
        if src.name != "roses-letters.jpg" and rng.random() < 0.4:
            im = ImageOps.mirror(im)
        cw, ch = im.size
        s = min(1.0, 1500 / max(cw, ch)) * rng.uniform(0.92, 1.0)
        im = im.resize((int(cw * s), int(ch * s)), Image.Resampling.LANCZOS)
        clean = Image.new("RGB", im.size)
        clean.putdata(list(im.getdata()))  # fresh image: no info/exif/icc carried over
        clean.save(out, format="JPEG", quality=rng.randint(86, 93), optimize=True)


def main() -> None:
    text = YAML_PATH.read_text(encoding="utf-8")
    cut = text.index("  - id: sasha-17\n")
    body_start = text.index("\nposts:\n") + len("\nposts:\n")
    keep = text[body_start:cut].rstrip() + "\n\n"

    posted_ids = {e.get("id") for e in json.loads(LOG_PATH.read_text()) if not e.get("dry_run")}
    sources_all = sorted(p for p in IMG.glob("*.jpg"))
    assert len(sources_all) == 32, len(sources_all)

    out = [HEADER, keep]
    out.append("  # ---------- SASHA 17-20 (published; captions fixed to Warsaw, ids kept) ----------\n")
    for i, lang in zip(range(17, 21), ["en", "ru", "en", "ru"]):
        f = f"sasha-{i:02d}.jpg"
        _, en, ru = NAMES[f]
        name = en if lang == "en" else ru
        out.append(block(f"sasha-{i}", f, name, lang, caption(lang, name, 40 + i, i)))

    out.append("  # ---------- BATCH-100 (EN/RU single-lang, #Warszawa) ----------\n")
    stats = {"batch_renamed": 0, "batch_posted_fixed": 0, "batch_dropped": []}
    for i in range(1, 101):
        src = sources_all[(i - 1) % 32]
        img = f"batch-100/batch-{i:03d}.jpg"
        pid_old = f"batch-{i:03d}"
        if src.name in EXCLUDE:
            if pid_old in posted_ids:
                raise SystemExit(f"{pid_old} is posted but excluded?")
            stats["batch_dropped"].append(pid_old)
            continue
        slug, en, ru = NAMES[src.name]
        lang = "en" if i % 2 else "ru"
        name = en if lang == "en" else ru
        cap = caption(lang, name, (i - 1) // 2, i)
        if pid_old in posted_ids:
            pid = pid_old
            stats["batch_posted_fixed"] += 1
        else:
            pid = f"b{i:03d}-{slug}-{lang}"
            stats["batch_renamed"] += 1
        out.append(block(pid, img, name, lang, cap))

    out.append("  # ---------- BATCH-50 (new clean variants, EN/RU single-lang, #Warszawa) ----------\n")
    OUT50.mkdir(exist_ok=True)
    src31 = [p for p in sources_all if p.name not in EXCLUDE]
    for i in range(1, 51):
        src = src31[(i * 7) % 31]  # spread across originals
        img = f"batch-50/var-{i:03d}.jpg"
        variant(src, 5000 + i, IMG / img)
        slug, en, ru = NAMES[src.name]
        lang = "en" if i % 2 else "ru"
        name = en if lang == "en" else ru
        cap = caption(lang, name, (i - 1) // 2 + 23, i + 2)
        out.append(block(f"v{i:03d}-{slug}-{lang}", img, name, lang, cap))

    YAML_PATH.write_text("".join(out).rstrip() + "\n", encoding="utf-8")
    print(json.dumps(stats))


if __name__ == "__main__":
    main()

# Цены на букеты — @july.botanique, Варшава

> Статус: entry-level тестовые цены, предложены Claude (claude-sonnet-5), ждут финального подтверждения VAC.
> 14.10.2026: по решению VAC все цены подняты на 20% с округлением до ближайшей цены на 9.

## Логика

- Мы новые, хотим первые заказы — цены занижены относительно обычных варшавских флористов (там mixed-букет среднего размера обычно 150–250 zł, premium/designer — 250–450 zł, монобукет из простых цветов — от 80–100 zł).
- Закупка — рынок, свои руки, без аренды шоурума — себестоимость низкая, можем позволить закупочную наценку x2–x2.5 вместо обычных x3–x4.
- Розы-буквы — самый премиальный формат (ручная набивка коробок), но даём низкий вход за счёт цены "за букву", а не за готовое слово — так дешевле решиться на первый заказ.
- Цель прайса — не прибыль с первого букета, а поток первых заказов и отзывов.

## Таблица по группам

| Группа | Диапазон, zł | Примеры |
|---|---|---|
| Малый/карманный (моноцветок, 1–2 вида, компактный) | 109–139 | fiery-crocosmia, brunia-sea-lavender, green-berries-statice, autumn-pocket |
| Средний (сборный букет, 3–5 видов, вазовый формат) | 159–239 | ember-dahlias, soft-morning, dahlia-calla-gentian, peach-callas |
| Большой / статусный (охапка, 40–50+ голов, диаметр XL) | 279–359 | crimson-still-life, ranunculus-carnival, coral-peonies |
| Спецформат — буквы из роз | 119 zł / буква | red-rose-letters |

## Цены по bouquet_key

| bouquet_key | zł | группа |
|---|---|---|
| fiery-crocosmia | 109 | small |
| brunia-sea-lavender | 109 | small |
| green-berries-statice | 109 | small |
| autumn-pocket | 119 | small |
| flame-parrot-flowers | 119 | small |
| chartreuse-cascade | 129 | small |
| burgundy-hydrangea-billy-balls | 129 | small |
| golden-chrysanthemums | 159 | medium |
| copper-chrysanthemums | 159 | medium |
| peach-pompon-dahlias | 169 | medium |
| ranunculus-chamomile-vase | 179 | medium |
| anthurium-dahlia-physalis | 189 | medium |
| soft-morning | 189 | medium |
| ember-dahlias | 199 | medium |
| burgundy-hydrangea-orange-dahlia | 199 | medium |
| pink-hydrangea-anthurium | 199 | medium |
| blush-hydrangea-anthurium | 199 | medium |
| blushing-peonies | 219 | medium |
| burgundy-hydrangea-stock | 219 | medium |
| deep-hydrangea-pompons | 219 | medium |
| carmine-and-smoke | 219 | medium |
| pink-rose-lilies | 219 | medium |
| dahlia-calla-gentian | 229 | medium |
| gentian-yellow-dahlia | 229 | medium |
| sunset-callas-sapphire | 229 | medium |
| gentian-pompon-dahlia | 229 | medium |
| peach-callas | 239 | medium |
| crimson-still-life | 279 | large |
| ranunculus-carnival | 299 | large |
| coral-peonies | 359 | large |
| red-rose-letters | 119/буква | спецформат |

Итого 31 bouquet_key размечен (flame-parrot-flowers и ranunculus-chamomile-vase добавлены из драфта Claude).

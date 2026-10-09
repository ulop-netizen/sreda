# Цены на букеты — @july.botanique, Варшава

> Статус: entry-level тестовые цены, предложены Claude (claude-sonnet-5), ждут финального подтверждения VAC.

## Логика

- Мы новые, хотим первые заказы — цены занижены относительно обычных варшавских флористов (там mixed-букет среднего размера обычно 150–250 zł, premium/designer — 250–450 zł, монобукет из простых цветов — от 80–100 zł).
- Закупка — рынок, свои руки, без аренды шоурума — себестоимость низкая, можем позволить закупочную наценку x2–x2.5 вместо обычных x3–x4.
- Розы-буквы — самый премиальный формат (ручная набивка коробок), но даём низкий вход за счёт цены "за букву", а не за готовое слово — так дешевле решиться на первый заказ.
- Цель прайса — не прибыль с первого букета, а поток первых заказов и отзывов.

## Таблица по группам

| Группа | Диапазон, zł | Примеры |
|---|---|---|
| Малый/карманный (моноцветок, 1–2 вида, компактный) | 89–119 | fiery-crocosmia, brunia-sea-lavender, green-berries-statice, autumn-pocket |
| Средний (сборный букет, 3–5 видов, вазовый формат) | 129–199 | ember-dahlias, soft-morning, dahlia-calla-gentian, peach-callas |
| Большой / статусный (охапка, 40–50+ голов, диаметр XL) | 229–299 | crimson-still-life, ranunculus-carnival, coral-peonies |
| Спецформат — буквы из роз | 99 zł / буква | red-rose-letters |

## Цены по bouquet_key

| bouquet_key | zł | группа |
|---|---|---|
| fiery-crocosmia | 89 | small |
| brunia-sea-lavender | 89 | small |
| green-berries-statice | 89 | small |
| autumn-pocket | 99 | small |
| flame-parrot-flowers | 99 | small |
| chartreuse-cascade | 109 | small |
| burgundy-hydrangea-billy-balls | 109 | small |
| golden-chrysanthemums | 129 | medium |
| copper-chrysanthemums | 129 | medium |
| peach-pompon-dahlias | 139 | medium |
| ranunculus-chamomile-vase | 149 | medium |
| anthurium-dahlia-physalis | 159 | medium |
| soft-morning | 159 | medium |
| ember-dahlias | 169 | medium |
| burgundy-hydrangea-orange-dahlia | 169 | medium |
| pink-hydrangea-anthurium | 169 | medium |
| blush-hydrangea-anthurium | 169 | medium |
| blushing-peonies | 179 | medium |
| burgundy-hydrangea-stock | 179 | medium |
| deep-hydrangea-pompons | 179 | medium |
| carmine-and-smoke | 179 | medium |
| pink-rose-lilies | 179 | medium |
| dahlia-calla-gentian | 189 | medium |
| gentian-yellow-dahlia | 189 | medium |
| sunset-callas-sapphire | 189 | medium |
| gentian-pompon-dahlia | 189 | medium |
| peach-callas | 199 | medium |
| crimson-still-life | 229 | large |
| ranunculus-carnival | 249 | large |
| coral-peonies | 299 | large |
| red-rose-letters | 99/буква | спецформат |

Итого 31 bouquet_key размечен (flame-parrot-flowers 99 и ranunculus-chamomile-vase 149 добавлены из драфта Claude).

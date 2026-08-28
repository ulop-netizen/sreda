# sreda — автопостинг цветов в Threads

Маленький бот: 5 раз в день берёт пост из пула `content/posts.yaml` и публикует
в Threads через официальный API. Крутится на бесплатном кроне GitHub Actions.

## Локальный запуск (сухой прогон)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # DRY_RUN=true уже стоит
.venv/bin/python -m src.post  # напечатает пост, ничего не опубликует
```

## Настройка Threads API (один раз)

1. **Threads → профессиональный аккаунт.** В приложении Threads: профиль →
   меню → Settings → Account → Switch to professional account. Категория —
   например «Florist».
2. **Meta Developer + приложение.** https://developers.facebook.com → войти →
   My Apps → Create App → выбрать use case **«Access the Threads API»**.
3. **Права.** В use case Threads добавить `threads_basic` и
   `threads_content_publish`.
4. **Redirect URI.** В настройках Threads use case добавить любой https-адрес
   (напр. страницу GitHub Pages этого репо). Нужен для OAuth.
5. **Токен.** Через кнопку «Generate access token» в дашборде **или** OAuth-ссылку
   получить короткоживущий токен, затем обменять на долгоживущий:
   ```bash
   .venv/bin/python scripts/exchange_token.py exchange <short_lived_token>
   ```
   Продление (раз в ~50 дней):
   ```bash
   .venv/bin/python scripts/exchange_token.py refresh <long_lived_token>
   ```
6. **Threads user ID.** `GET https://graph.threads.net/v1.0/me?fields=id,username&access_token=<token>`
7. Заполнить `.env`: `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN`, `THREADS_APP_SECRET`.

## Публикация по-настоящему

Локально: поставить `DRY_RUN=false` в `.env`, запустить `.venv/bin/python -m src.post`.

На GitHub: Settings → Secrets and variables → Actions
- Secrets: `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN`
- Variables: `DRY_RUN=false` (пока не готов — держи `true` или не создавай)

Расписание и часовой пояс правятся в `.github/workflows/post.yml` (cron в UTC).

# Internet Shop

Прототип интернет-магазина на Django с уведомлениями о заказах в Telegram.

## Запуск с нуля

1. Клонировать репозиторий и перейти в папку проекта:
   ```bash
   git clone https://github.com/bonanoz/internet-shop.git
   cd internet-shop/internetshop
   ```

2. Создать и активировать виртуальное окружение:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Установить PostgreSQL (если ещё не стоит) и создать базу данных:
   ```sql
   CREATE DATABASE internetshop;
   ```

5. Скопировать `.env.example` в `.env` и заполнить своими значениями:
   ```bash
   cp .env.example .env
   ```
   - `BOT_TOKEN` — токен бота, получить у [@BotFather](https://t.me/BotFather) в Telegram
   - `CHAT_ID` — id чата/канала, куда будут приходить уведомления о заказах
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — параметры подключения к PostgreSQL

6. Накатить миграции и создать администратора:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. Запустить сервер:
   ```bash
   python manage.py runserver
   ```
   Магазин: http://127.0.0.1:8000/
   Админка: http://127.0.0.1:8000/admin/

## Важно

`.env` никогда не коммитится в git. Сохрани его отдельно (например в менеджере
паролей), чтобы не терять токены при переустановке системы.

# Структура проекту Flask

Проект розділено на модулі для кращої організації коду.

## Структура файлів

```
web_flask/
├── app.py                 # Головний файл додатку (створює Flask app)
├── config.py              # Конфігурація (API URLs, timeouts, paths)
├── utils/                 # Утиліти та допоміжні функції
│   ├── __init__.py        # Експорт всіх утиліт
│   ├── api_client.py      # API клієнт для C++ backend
│   ├── database.py        # Робота з SQLite БД
│   ├── decorators.py      # Декоратори (login_required, admin_required)
│   ├── helpers.py         # Допоміжні функції (build_roster, get_team_by_name)
│   └── teams.py           # Робота з командами
├── routes/                # Blueprints для різних сторінок
│   ├── __init__.py        # Експорт всіх blueprints
│   ├── auth.py            # Авторизація (login, register, logout)
│   ├── dashboard.py       # Головна сторінка з описом проекту
│   ├── matches.py         # Матчі та голосування
│   ├── players.py         # Сторінка гравців
│   ├── stats.py           # Статистика матчів
│   ├── admin.py           # Адмін функції (додавання команд, гравців)
│   └── health.py          # Health check endpoint
└── templates/             # HTML шаблони
```

## Основні модулі

### `app.py`
- Створює Flask додаток
- Реєструє всі blueprints
- Налаштовує before_request handlers
- Ініціалізує базу даних

### `config.py`
- Зберігає всі конфігураційні змінні
- API URLs, timeouts, cache TTL
- Шляхи до файлів та директорій

### `utils/api_client.py`
- `_get()` - GET запити до API з кешуванням
- `_post()` - POST запити до API
- `_invalidate_cache()` - очищення кешу
- `get_cached_stats()` - отримання статистики з кешем

### `utils/database.py`
- `get_db()` - отримання підключення до БД
- `close_db()` - закриття підключення
- `init_user_db()` - ініціалізація таблиць користувачів

### `utils/decorators.py`
- `@login_required` - вимагає авторизації
- `@admin_required` - вимагає права адміна

### `utils/helpers.py`
- `get_team_by_name()` - пошук команди за назвою
- `build_roster()` - побудова розташування гравців на полі

### `utils/teams.py`
- `_normalize()` - нормалізація назв для пошуку
- `_load_teams_from_api()` - завантаження команд з API
- `sync_teams_and_players()` - синхронізація даних

### `routes/`
Кожен файл містить blueprint з роутами для конкретної функціональності:
- `auth.py` - `/login`, `/register`, `/logout`
- `dashboard.py` - `/` (головна сторінка)
- `matches.py` - `/matches`, `/vote`, `/matches/add`
- `players.py` - `/players`
- `stats.py` - `/stats`, `/matches/close`, `/matches/update-stats`
- `admin.py` - `/teams/add`, `/players/add`, `/api/check-vote`
- `health.py` - `/health`

## Переваги нової структури

1. **Модульність** - кожен модуль відповідає за свою функціональність
2. **Читабельність** - легше знайти потрібний код
3. **Підтримка** - простіше додавати нові функції
4. **Тестування** - можна тестувати модулі окремо
5. **Масштабованість** - легко додавати нові blueprints


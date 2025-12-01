# Версія проекту - Статичні HTML файли

**Дата:** 1 грудня 2025  
**Статус:** ✅ Працює стабільно

## Опис

Проект використовує статичні HTML файли з JavaScript для завантаження даних через C++ backend API. Flask віддає статичні HTML файли замість рендерингу Jinja2 templates.

## Структура проекту

```
web_flask/
├── app.py                 # Головний Flask app (110 рядків)
├── config.py              # Конфігурація
├── utils/                 # Утиліти
│   ├── __init__.py
│   ├── api_client.py      # API клієнт для C++ backend
│   ├── database.py        # Робота з SQLite БД
│   ├── decorators.py      # Декоратори (login_required, admin_required)
│   ├── helpers.py         # Допоміжні функції
│   └── teams.py           # Робота з командами
├── routes/                # Blueprints (віддають статичні HTML)
│   ├── __init__.py
│   ├── auth.py            # Авторизація
│   ├── dashboard.py       # Головна сторінка
│   ├── matches.py         # Матчі
│   ├── players.py         # Гравці
│   ├── stats.py           # Статистика
│   ├── admin.py           # Адмін функції
│   └── health.py          # Health check
└── static/                # Статичні HTML файли
    ├── index.html          # Головна сторінка
    ├── matches.html        # Матчі та голосування
    ├── players.html        # Список гравців
    ├── stats.html          # Статистика
    ├── health.html         # Стан API
    ├── login.html          # Авторизація
    ├── register.html       # Реєстрація
    ├── app.js              # API клієнт та утиліти
    ├── matches.js          # Логіка для матчів
    ├── style.css           # Основні стилі
    ├── modal.css           # Стилі для модальних вікон
    └── stats.css           # Стилі для статистики
```

## Ключові особливості

### 1. Статичні HTML файли
- Всі сторінки - статичні HTML файли в папці `static/`
- Flask routes віддають HTML через `send_file()`
- JavaScript завантажує дані через C++ API

### 2. API клієнт (app.js)
- Клас `APIClient` для GET/POST запитів
- Автоматичне завантаження глобальної статистики
- Обробка помилок та кешування

### 3. Flask Routes
- Всі routes віддають статичні HTML файли
- Мінімальна логіка на сервері
- Bootstrap для ініціалізації БД та синхронізації даних

### 4. Структура коду
- Модульна організація (utils/, routes/)
- Blueprints для різних функцій
- Конфігурація винесена в окремий файл

## Налаштування Flask

```python
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

- Статичні файли доступні через `/static/`
- CSS/JS автоматично віддаються Flask
- Заголовки для кешування налаштовані

## API Endpoints (C++ Backend)

Проект використовує наступні endpoints:
- `/api/teams` - список команд
- `/api/players` - список гравців
- `/api/matches` - список матчів
- `/api/votes/{match_id}` - голоси за матч
- `/api/stats` - глобальна статистика
- `/api/dashboard` - дані для dashboard
- `/api/matches-page` - дані для сторінки матчів
- `/api/players-page` - дані для сторінки гравців
- `/api/stats-page` - дані для сторінки статистики

## Як запустити

1. Запустити C++ backend на порту 8080
2. Запустити Flask frontend:
   ```bash
   cd web_flask
   python app.py
   ```
3. Відкрити `http://localhost:5000`

## Переваги цієї версії

✅ Швидке завантаження (статичні файли кешуються)  
✅ Простий деплой (можна використовувати будь-який веб-сервер)  
✅ Модульна структура коду  
✅ Легко підтримувати та розширювати  
✅ Всі дані динамічні через API  

## Відомі обмеження

⚠️ Авторизація поки що не працює для статичних HTML (потрібен Flask для сесій)  
⚠️ Голосування потребує авторизації через Flask  
⚠️ Адмін функції потребують авторизації  

## Файли для збереження

Всі файли в папках:
- `web_flask/app.py`
- `web_flask/config.py`
- `web_flask/utils/`
- `web_flask/routes/`
- `web_flask/static/`

## Примітки

- CSS файли доступні через `/static/style.css`
- JavaScript файли доступні через `/static/app.js`
- Всі HTML файли використовують абсолютні шляхи `/static/...`
- Flask автоматично віддає статичні файли з папки `static/`


# Система голосування за гравців футбольного матчу

Курсовий проєкт з ООП: повноцінна веб-система для підрахунку голосів у режимі реального часу з авторизацією користувачів та інтерактивним футбольним полем.

## Архітектура

- **`server_cpp`** – модульний C++17 REST API (класи: `Player`, `Match`, `VotingService`, `JsonFileStore`, `HttpServer`).
- **`web_flask`** – сучасний інтерфейс на Flask з шаблонами Jinja2 та кастомним UI.

Докладніше: `ARCHITECTURE.md`.

## Швидкий старт

### Локальний запуск

```powershell
./install_dependencies.ps1   # встановити залежності
./start_all.ps1              # запустити backend (8080) і фронт (5000)
```

### Docker запуск (рекомендовано)

```powershell
docker-compose up --build    # запустити всі сервіси в контейнерах
```

Докладніше в `DOCKER_README.md` та `SETUP_GUIDE.md`.

## API

- `GET /api/players`, `POST /api/players/add`
- `GET /api/matches`, `POST /api/matches/add`
- `GET /api/votes/{matchId}`
- `POST /api/vote`
- `GET /api/stats`

Приклади – у `API_EXAMPLES.md`.

## Можливості веб-інтерфейсу (Flask)

1. **Головна** – футбольне поле з 22 гравцями (Real Madrid, Barcelona, Man City, Bayern). Голосування кліком по позиції.
2. **Гравці** – перегляд усіх футболістів, автоматична синхронізація з базою справжніх складів, ручне додавання (лише адмін).
3. **Матчі** – створення голосувань адміністратором зі списку команд.
4. **Статистика** – топ-10 гравців та агреговані показники по матчах.
5. **Стан API** – перевірка відповіді C++ сервера.
6. **Реєстрація / Вхід** – ролі *fan* (звичайний користувач) та *admin* (логін `admin`, пароль `admin123` за замовчуванням). Голосування доступне тільки після авторизації.

## Інфраструктура та тестування

- **Логування** – автоматичний запис у файли `logs/app.log` та `logs/error.log` з ротацією (10MB, 10 бекапів).
- **Юніт-тести** – запуск: `python web_flask/run_tests.py` (8 тестів для основних endpoint'ів).
- **Docker** – повна контейнеризація з `docker-compose.yml` для швидкого розгортання.
- **CI/CD Ready** – конфігурації `.gitignore` та `.dockerignore` для production deployment.

## Структура

```
server_cpp/   # C++ код (src/models, services, storage, http)
web_flask/    # Flask застосунок (templates, static, start.py)
start_backend.* / start_frontend.* / start_all.ps1
ARCHITECTURE.md, PROJECT_STRUCTURE.md, SETUP_GUIDE.md
```

## Тестування та моніторинг

```powershell
# Запуск тестів локально
python web_flask/run_tests.py

# Запуск тестів у Docker
docker-compose exec flask python run_tests.py

# Перегляд логів
tail -f web_flask/logs/app.log
tail -f web_flask/logs/error.log
```

## Подальший розвиток

- Перенести всі дані у повноцінну БД (наприклад PostgreSQL).
- Додати live-оновлення через WebSocket.
- Передбачити кабінет модератора для створення власних клубів і складів.
- Розширити coverage тестів до 90%+.
- Налаштувати CI/CD pipeline (GitHub Actions).

Проєкт створено для навчальних цілей та демонструє принципи ООП на практиці.

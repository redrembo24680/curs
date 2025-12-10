# Docker Setup

## Запуск проєкту через Docker

### Попередні вимоги
- Docker Desktop встановлено
- Docker Compose встановлено

### Запуск

1. **Побудувати та запустити контейнери:**
```bash
docker-compose up --build
```

2. **Запустити у фоновому режимі:**
```bash
docker-compose up -d
```

3. **Зупинити контейнери:**
```bash
docker-compose down
```

4. **Переглянути логи:**
```bash
docker-compose logs -f flask
```

### Доступ до сервісів

- Flask Frontend: http://localhost:5000
- C++ Backend: http://localhost:8080

### Примітки

- Flask автоматично перезавантажується при зміні коду
- Логи зберігаються у volume `flask_logs`
- База даних SQLite зберігається в контейнері

## Тестування

Запуск юніт-тестів всередині контейнера:
```bash
docker-compose exec flask python -m pytest tests/
```

Або локально:
```bash
cd web_flask
python -m pytest tests/
```

## Логування

Логи зберігаються в директорії `web_flask/logs/`:
- `app.log` - всі логи
- `error.log` - тільки помилки

Перегляд логів:
```bash
# В реальному часі
tail -f web_flask/logs/app.log

# Останні 100 рядків
tail -n 100 web_flask/logs/app.log
```

# Інструкції по тестуванню системи голосування

## 1. Запуск юніт-тестів Flask

### В контейнері:
```bash
docker exec curs-flask-1 python run_tests.py
```

### Локально (якщо Python встановлено):
```bash
cd web_flask
python run_tests.py
```

## 2. Тестування API голосування

### Використання готового скрипта PowerShell:
```powershell
.\test_voting.ps1
```

### Ручне тестування через curl/Invoke-RestMethod:

#### 1. Отримати список активних матчів:
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/matches-page" -Method Get
```

#### 2. Отримати список гравців:
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/players" -Method Get
```

#### 3. Проголосувати за гравця:
```powershell
$voteData = @{
    match_id = 11
    player_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/vote" -Method Post -Body $voteData -ContentType "application/json"
```

#### 4. Перевірити голоси для конкретного матчу:
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/votes?match_id=11" -Method Get
```

#### 5. Отримати загальну статистику:
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/stats" -Method Get
```

## 3. Тестування через веб-інтерфейс

1. Відкрийте браузер: http://localhost:5000
2. Перейдіть на сторінку "Матчі"
3. Оберіть активний матч
4. Проголосуйте за гравця
5. Перевірте результати на сторінці "Статистика"

## 4. Перевірка роботи контейнерів

### Статус контейнерів:
```powershell
docker ps
```

### Логи Flask:
```powershell
docker logs curs-flask-1
```

### Логи C++ Backend:
```powershell
docker logs curs-cpp_backend-1
```

### Перезапуск контейнерів:
```powershell
docker-compose restart
```

## 5. API Endpoints

| Метод | Endpoint | Опис |
|-------|----------|------|
| GET | `/api/teams` | Список всіх команд |
| GET | `/api/players` | Список всіх гравців |
| GET | `/api/matches-page` | Активні матчі з інформацією |
| POST | `/api/vote` | Проголосувати (body: `{match_id, player_id}`) |
| GET | `/api/votes?match_id=X` | Голоси для матчу X |
| GET | `/api/stats` | Загальна статистика |
| POST | `/api/close-match` | Закрити матч (body: `{match_id}`) |

## 6. Заповнення бази даних тестовими даними

Якщо потрібно заповнити базу даних:
```powershell
python populate_db.py
```

## 7. Перевірка бази даних SQLite

### В контейнері:
```bash
docker exec -it curs-cpp_backend-1 sqlite3 /app/data/voting.db "SELECT COUNT(*) FROM players;"
```

### Локально:
```bash
sqlite3 server_cpp/data/voting.db "SELECT * FROM teams;"
```

## Troubleshooting

### Контейнер не запускається:
```powershell
docker-compose down
docker-compose up --build -d
```

### База даних порожня:
Перевірте volume mapping в `docker-compose.yml` та переконайтеся, що змінна `DATA_DIR=/app/data` встановлена.

### Помилки з'єднання:
- Flask: http://localhost:5000
- C++ Backend: http://localhost:8080
- Перевірте, чи відкриті порти: `docker ps`

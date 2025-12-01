# Voting System Backend - SQLite Version

## Опис

C++ бекенд для системи голосування з використанням SQLite бази даних.

## Структура

- `src/` - вихідний код
- `data/voting.db` - SQLite база даних
- `build/` - збірка проєкту

## Збірка

```powershell
cd build
cmake ..
cmake --build . --config Release
```

## Запуск

```powershell
.\build\bin\Release\voting_server.exe
```

## База даних

Всі дані зберігаються в `data/voting.db`:
- Команди (teams)
- Гравці (players)
- Матчі (matches)
- Голоси (votes)
- Статистика матчів (match_stats)

## Перевірка бази даних

```powershell
python check_database.py data\voting.db
```

## Заповнення бази даних

Якщо потрібно заповнити базу даних з JSON файлів:

```powershell
python ..\web_flask\migrate_json_to_sqlite.py data data\voting.db
```

## API Endpoints

- `GET /api/teams` - список команд
- `GET /api/players` - список гравців
- `GET /api/matches` - список матчів
- `GET /api/stats` - загальна статистика
- `GET /api/match-stats` - статистика матчів
- `POST /api/vote` - проголосувати
- `POST /api/teams/add` - додати команду
- `POST /api/players/add` - додати гравця
- `POST /api/matches/add` - додати матч



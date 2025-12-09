#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# Підключаємось до бази
db_path = r"server_cpp\data\voting.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Команди
teams = [
    (1, "Динамо"),
    (2, "Шахтар"),
    (3, "Мілан"),
    (4, "Реал"),
    (5, "Ман Юнайтед"),
    (6, "Ліверпуль"),
]

for team_id, name in teams:
    c.execute('''INSERT OR REPLACE INTO teams (id, name) 
                 VALUES (?, ?)''', (team_id, name))

# Гравці (66 гравців)
players = []
player_id = 1

positions = ["Вратар", "Захисник", "Захисник", "Захисник", "Захисник",
             "Півзахисник", "Півзахисник", "Півзахисник", "Нападник", "Нападник", "Нападник"]

# Динамо (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Динамо {i+1}", positions[i], 1))
    player_id += 1

# Шахтар (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Шахтар {i+1}", positions[i], 2))
    player_id += 1

# Мілан (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Мілан {i+1}", positions[i], 3))
    player_id += 1

# Реал (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Реал {i+1}", positions[i], 4))
    player_id += 1

# Ман Юнайтед (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Ман Юнайтед {i+1}", positions[i], 5))
    player_id += 1

# Ліверпуль (11 гравців)
for i in range(11):
    players.append((player_id, f"Гравець Ліверпуль {i+1}", positions[i], 6))
    player_id += 1

for pid, name, position, team_id in players:
    c.execute('''INSERT OR REPLACE INTO players (id, name, position, team_id) 
                 VALUES (?, ?, ?, ?)''', (pid, name, position, team_id))

conn.commit()
conn.close()

print("✓ База даних заповнена успішно!")
print(f"✓ Команд: {len(teams)}")
print(f"✓ Гравців: {len(players)}")

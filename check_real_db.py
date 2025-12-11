import sqlite3

conn = sqlite3.connect('/app/database.sqlite')
cursor = conn.cursor()
cursor.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name='user_votes'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("No table found")
conn.close()

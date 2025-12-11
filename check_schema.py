import sqlite3

DB_PATH = "web_flask/data/database.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_votes'")
schema = cursor.fetchone()

if schema:
    print("=== user_votes table schema ===")
    print(schema[0])
else:
    print("Table user_votes does not exist!")

conn.close()

import sqlite3

# Check OLD database (wrong path)
print("=== OLD database (/app/database.sqlite) ===")
conn_old = sqlite3.connect('/app/database.sqlite')
cursor = conn_old.cursor()
cursor.execute("SELECT COUNT(*) FROM user_votes")
count_old = cursor.fetchone()[0]
print(f"user_votes records: {count_old}")

if count_old > 0:
    cursor.execute("SELECT * FROM user_votes")
    for row in cursor.fetchall():
        print(row)
conn_old.close()

print("\n=== NEW database (/app/data/database.sqlite) ===")
conn_new = sqlite3.connect('/app/data/database.sqlite')
cursor = conn_new.cursor()
cursor.execute("SELECT COUNT(*) FROM user_votes")
count_new = cursor.fetchone()[0]
print(f"user_votes records: {count_new}")

if count_new > 0:
    cursor.execute("SELECT * FROM user_votes")
    for row in cursor.fetchall():
        print(row)
conn_new.close()

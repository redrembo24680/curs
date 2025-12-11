import sqlite3

conn = sqlite3.connect('/app/data/database.sqlite')
cursor = conn.cursor()

# Try to insert a vote
try:
    cursor.execute(
        "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
        (1, 1, 20)
    )
    conn.commit()
    print("INSERT successful!")
    
    # Check what we inserted
    cursor.execute("SELECT * FROM user_votes WHERE user_id=1 AND match_id=1")
    result = cursor.fetchone()
    print(f"Record: {result}")
    
except sqlite3.IntegrityError as e:
    print(f"IntegrityError: {e}")
    conn.rollback()

# Now try to insert SAME user_id and match_id but DIFFERENT player
try:
    cursor.execute(
        "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
        (1, 1, 21)  # Different player!
    )
    conn.commit()
    print("Second INSERT successful - BUG! Should have failed!")
except sqlite3.IntegrityError as e:
    print(f"Second INSERT failed as expected: {e}")
    conn.rollback()

conn.close()

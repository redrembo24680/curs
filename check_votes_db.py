#!/usr/bin/env python3
"""Check votes in Flask database."""
import sqlite3

def check_votes():
    conn = sqlite3.connect('web_flask/data/database.sqlite')
    conn.row_factory = sqlite3.Row
    
    print("=== user_votes table ===")
    rows = conn.execute('SELECT * FROM user_votes').fetchall()
    print(f'Total records: {len(rows)}')
    for r in rows:
        print(f"  user_id={r['user_id']}, match_id={r['match_id']}, player_id={r['player_id']}")
    
    conn.close()

if __name__ == '__main__':
    check_votes()

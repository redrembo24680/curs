#!/usr/bin/env python3
"""Recreate user_votes table with correct constraint."""
import sqlite3
import os

DB_PATH = 'web_flask/data/database.sqlite'

def recreate_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    # Drop old table
    print("Dropping old user_votes table...")
    conn.execute("DROP TABLE IF EXISTS user_votes")
    
    # Create new table with correct constraint
    print("Creating new user_votes table with UNIQUE(user_id, match_id)...")
    conn.execute("""
        CREATE TABLE user_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, match_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ Table recreated successfully!")
    print("  Constraint: UNIQUE(user_id, match_id)")
    print("  This means: One vote per user per match")

if __name__ == '__main__':
    recreate_table()

"""Database utilities."""
import sqlite3
from typing import Any

from flask import g
from werkzeug.security import generate_password_hash

from config import DB_PATH


def get_db() -> sqlite3.Connection:
    """Get database connection from Flask g."""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def close_db(_: Any) -> None:
    """Close database connection."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_user_db() -> None:
    """Initialize user database tables."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'fan'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, player_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    # Comments table for matches
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS match_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    # Posts table for news/announcements
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, 'admin')",
            ("admin", generate_password_hash("admin123")),
        )
        conn.commit()
    conn.close()


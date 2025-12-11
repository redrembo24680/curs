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
    try:
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
                UNIQUE(user_id, match_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        # Cache table for players (synced from C++ API)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cached_players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                team_id INTEGER,
                votes INTEGER DEFAULT 0,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Cache table for matches (synced from C++ API)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cached_matches (
            id INTEGER PRIMARY KEY,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            date TEXT,
            is_active BOOLEAN DEFAULT 1,
            team1_goals INTEGER DEFAULT 0,
            team2_goals INTEGER DEFAULT 0,
            team1_possession INTEGER DEFAULT 50,
            team2_possession INTEGER DEFAULT 50,
            team1_shots INTEGER DEFAULT 0,
            team2_shots INTEGER DEFAULT 0,
            team1_shots_on_target INTEGER DEFAULT 0,
            team2_shots_on_target INTEGER DEFAULT 0,
            team1_corners INTEGER DEFAULT 0,
            team2_corners INTEGER DEFAULT 0,
            team1_fouls INTEGER DEFAULT 0,
            team2_fouls INTEGER DEFAULT 0,
            team1_yellow_cards INTEGER DEFAULT 0,
            team2_yellow_cards INTEGER DEFAULT 0,
            team1_red_cards INTEGER DEFAULT 0,
            team2_red_cards INTEGER DEFAULT 0,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Add new columns if they don't exist (for existing databases)
        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_goals INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_goals INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_possession INTEGER DEFAULT 50")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_possession INTEGER DEFAULT 50")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_shots INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_shots INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_shots_on_target INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_shots_on_target INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_corners INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_corners INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_fouls INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_fouls INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_yellow_cards INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_yellow_cards INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team1_red_cards INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute(
                "ALTER TABLE cached_matches ADD COLUMN team2_red_cards INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        # Cache table for teams (synced from C++ API)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cached_teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    finally:
        conn.close()

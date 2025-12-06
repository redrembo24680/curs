#!/usr/bin/env python
"""Initialize database with new schema."""
import sys
import os

# Add web_flask to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_flask'))

from utils.database import init_user_db

# Initialize database
init_user_db()
print("✓ БД успішно ініціалізована з новою схемою (UNIQUE constraint на user_id, player_id)")

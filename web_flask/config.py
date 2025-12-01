"""Configuration settings for the Flask application."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = BASE_DIR / "database.sqlite"
SESSION_DIR = BASE_DIR / "flask_session"
SESSION_DIR.mkdir(exist_ok=True)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api")
REQUEST_TIMEOUT = float(os.getenv("API_TIMEOUT", "3.0"))
CACHE_TTL = float(os.getenv("API_CACHE_TTL", "5.0"))

# Flask Configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
SESSION_FILE_DIR = str(SESSION_DIR)

# Stats Cache Configuration
STATS_CACHE_TTL = 10.0  # Cache stats for 10 seconds


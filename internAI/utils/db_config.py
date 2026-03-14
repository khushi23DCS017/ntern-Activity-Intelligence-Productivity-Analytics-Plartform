# pyre-ignore-all-errors
"""
PostgreSQL database configuration for SQLAlchemy-based queries.
Uses DATABASE_URL from .env for a single connection string.
Falls back to individual env vars or config.py defaults.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load .env from project root
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed, use env vars directly


def get_db_uri():
    """
    Return SQLAlchemy-compatible PostgreSQL URI.
    Priority: DATABASE_URL env var > DB_CONNECTION_STRING > individual vars > config.py defaults.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("DB_CONNECTION_STRING")
    if url:
        # Ensure psycopg2 driver for SQLAlchemy
        if url.startswith("postgresql://") and "psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # Fallback: build from individual vars or config.py defaults
    try:
        from config import DB_CONFIG
        host = os.getenv('DB_HOST', DB_CONFIG.get('host', 'localhost'))
        db   = os.getenv('DB_NAME', DB_CONFIG.get('database', 'intern_analytics'))
        user = os.getenv('DB_USER', DB_CONFIG.get('user', 'postgres'))
        pwd  = os.getenv('DB_PASSWORD', DB_CONFIG.get('password', '1234'))
        port = os.getenv('DB_PORT', '5432')
    except ImportError:
        host = os.getenv('DB_HOST', 'localhost')
        db   = os.getenv('DB_NAME', 'intern_analytics')
        user = os.getenv('DB_USER', 'postgres')
        pwd  = os.getenv('DB_PASSWORD', '')
        port = os.getenv('DB_PORT', '5432')

    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

"""SQLite database connection and initialization."""
import os
import sqlite3
import json
from pathlib import Path

from backend.config import DATABASE_PATH


def get_db():
    """Get a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    """Initialize the database with schema."""
    conn = get_db()
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r") as f:
        conn.executescript(f.read())

    # Migration: add groundedness column if not present
    try:
        conn.execute("SELECT groundedness FROM memories LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE memories ADD COLUMN groundedness TEXT DEFAULT '{}'")
        conn.commit()

    # Migration: create memory_embeddings table if not present
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_embeddings (
            memory_id TEXT PRIMARY KEY,
            embedding TEXT NOT NULL,
            text_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memory_id) REFERENCES memories(id)
        )
    """)
    conn.commit()

    conn.close()


def dict_from_row(row):
    """Convert a sqlite3.Row to a dictionary."""
    if row is None:
        return None
    d = dict(row)
    # Parse JSON fields
    json_fields = ['detection_reasons', 'reasoning', 'missing_info', 'guardrail_flags', 'groundedness', 'details']
    for field in json_fields:
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d

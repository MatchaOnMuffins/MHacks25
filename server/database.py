import sqlite3
import os
import time
from contextlib import contextmanager

os.makedirs("database", exist_ok=True)
DB_PATH = "database/feedback.db"

def init_database():
    """Initialize the database and create the feedback table if it doesn't exist"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def add_entry(feedback_text: str) -> int:
    """Add a new entry to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (feedback, timestamp) VALUES (?, ?)",
            (feedback_text, int(time.time()))
        )
        conn.commit()
        return cursor.lastrowid
from typing import Optional, Tuple

def get_most_recent_entry() -> Optional[Tuple[str, int]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, feedback, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            return None
        return (row["feedback"], row["timestamp"])

init_database()

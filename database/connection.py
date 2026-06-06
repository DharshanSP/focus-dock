import sqlite3
import os
from pathlib import Path

DB_DIR = Path.home() / ".deskreminder"
DB_PATH = DB_DIR / "deskreminder.db"

def get_db_connection():
    """Returns a connection to the SQLite database, ensuring directory exists."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

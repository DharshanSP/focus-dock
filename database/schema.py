from database.connection import get_db_connection

def initialize_database():
    """Initializes SQLite schema, creating tables and inserting default settings."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create reminders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT NOT NULL,       -- YYYY-MM-DD
        due_time TEXT NOT NULL,       -- HH:MM
        priority TEXT NOT NULL,       -- Low, Medium, High, Critical
        category TEXT NOT NULL,       -- Study, Work, Personal, Fitness, Finance, Custom
        repeat_type TEXT NOT NULL,    -- None, Daily, Weekly, Monthly, Yearly, Custom
        repeat_interval INTEGER DEFAULT 1,
        completed INTEGER DEFAULT 0,  -- 0 or 1
        is_sticky INTEGER DEFAULT 0,  -- 0 or 1
        sticky_x INTEGER,
        sticky_y INTEGER,
        sticky_width INTEGER DEFAULT 250,
        sticky_height INTEGER DEFAULT 250,
        sticky_theme TEXT DEFAULT 'Yellow', -- Yellow, Blue, Green, Pink, Dark
        sticky_pinned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    # Create pomodoro_sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pomodoro_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mode TEXT NOT NULL,           -- 25/5, 50/10, Custom
        duration INTEGER NOT NULL,    -- duration in seconds
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert default settings if they don't exist
    default_settings = [
        ("theme", "glass"),
        ("startup_with_windows", "false"),
        ("notification_sound", "true"),
        ("always_on_top", "false"),
        ("default_duration", "30"),
        ("date_format", "YYYY-MM-DD"),
        ("time_format", "HH:MM")
    ]
    for key, val in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")

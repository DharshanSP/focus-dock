from database.connection import get_db_connection
from datetime import datetime

class PomodoroRepository:
    def create_session(self, mode: str, duration_sec: int) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pomodoro_sessions (mode, duration) VALUES (?, ?)",
            (mode, duration_sec)
        )
        conn.commit()
        conn.close()

    def get_completed_today_count(self) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM pomodoro_sessions WHERE date(completed_at) = date('now', 'localtime')"
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_history(self, limit: int = 10) -> list[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT mode, duration, completed_at FROM pomodoro_sessions ORDER BY completed_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"mode": r["mode"], "duration": r["duration"], "completed_at": r["completed_at"]} for r in rows]

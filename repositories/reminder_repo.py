from database.connection import get_db_connection
from models.reminder import Reminder

class ReminderRepository:
    def create(self, reminder: Reminder) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (
                title, description, due_date, due_time, priority, category,
                repeat_type, repeat_interval, completed, is_sticky,
                sticky_x, sticky_y, sticky_width, sticky_height, sticky_theme, sticky_pinned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reminder.title, reminder.description, reminder.due_date, reminder.due_time,
            reminder.priority, reminder.category, reminder.repeat_type, reminder.repeat_interval,
            1 if reminder.completed else 0, 1 if reminder.is_sticky else 0,
            reminder.sticky_x, reminder.sticky_y, reminder.sticky_width, reminder.sticky_height,
            reminder.sticky_theme, 1 if reminder.sticky_pinned else 0
        ))
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id

    def get_by_id(self, reminder_id: int) -> Reminder | None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        conn.close()
        return Reminder.from_row(row) if row else None

    def get_all(self, search: str = "", filter_by: str = "All", category: str = "All", sort_by: str = "Time") -> list[Reminder]:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM reminders WHERE 1=1"
        params = []

        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Filters
        if filter_by == "Today":
            query += " AND due_date = date('now', 'localtime') AND completed = 0"
        elif filter_by == "Upcoming":
            query += " AND due_date > date('now', 'localtime') AND completed = 0"
        elif filter_by == "Completed":
            query += " AND completed = 1"
        elif filter_by == "High Priority":
            query += " AND (priority = 'High' OR priority = 'Critical') AND completed = 0"
        
        if category != "All":
            query += " AND category = ?"
            params.append(category)

        # Sorting
        if sort_by == "Time":
            query += " ORDER BY due_date ASC, due_time ASC"
        elif sort_by == "Priority":
            query += " ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 END"
        elif sort_by == "Date Created":
            query += " ORDER BY created_at DESC"
        elif sort_by == "Alphabetical":
            query += " ORDER BY title COLLATE NOCASE ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Reminder.from_row(row) for row in rows]

    def update(self, reminder: Reminder) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders SET
                title = ?, description = ?, due_date = ?, due_time = ?,
                priority = ?, category = ?, repeat_type = ?, repeat_interval = ?,
                completed = ?, is_sticky = ?, sticky_x = ?, sticky_y = ?,
                sticky_width = ?, sticky_height = ?, sticky_theme = ?, sticky_pinned = ?
            WHERE id = ?
        """, (
            reminder.title, reminder.description, reminder.due_date, reminder.due_time,
            reminder.priority, reminder.category, reminder.repeat_type, reminder.repeat_interval,
            1 if reminder.completed else 0, 1 if reminder.is_sticky else 0,
            reminder.sticky_x, reminder.sticky_y, reminder.sticky_width, reminder.sticky_height,
            reminder.sticky_theme, 1 if reminder.sticky_pinned else 0,
            reminder.id
        ))
        conn.commit()
        conn.close()

    def delete(self, reminder_id: int) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()

    def get_sticky_notes(self) -> list[Reminder]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE is_sticky = 1")
        rows = cursor.fetchall()
        conn.close()
        return [Reminder.from_row(row) for row in rows]

    def get_pending_active_at(self, current_date: str, current_time: str) -> list[Reminder]:
        """Gets all non-completed reminders due at or before the specified date and time."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reminders WHERE (due_date < ? OR (due_date = ? AND due_time <= ?)) AND completed = 0",
            (current_date, current_date, current_time)
        )
        rows = cursor.fetchall()
        conn.close()
        return [Reminder.from_row(row) for row in rows]

from datetime import datetime, timedelta, date
from models.reminder import Reminder
from repositories.reminder_repo import ReminderRepository

class ReminderService:
    def __init__(self, repository: ReminderRepository):
        self.repository = repository

    def calculate_next_occurrence(self, current_date_str: str, repeat_type: str, interval: int = 1) -> str:
        """Calculates next occurrence date string (YYYY-MM-DD) based on repeat settings."""
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
        
        if repeat_type == "Daily":
            next_date = current_date + timedelta(days=interval)
        elif repeat_type == "Weekly":
            next_date = current_date + timedelta(weeks=interval)
        elif repeat_type == "Monthly":
            # Add calendar months
            year = current_date.year + (current_date.month + interval - 1) // 12
            month = (current_date.month + interval - 1) % 12 + 1
            day = min(current_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            next_date = date(year, month, day)
        elif repeat_type == "Yearly":
            # Add calendar years
            year = current_date.year + interval
            month = current_date.month
            day = min(current_date.day, 29 if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            next_date = date(year, month, day)
        else:
            next_date = current_date

        return next_date.strftime("%Y-%m-%d")

    def complete_reminder(self, reminder_id: int) -> None:
        """Marks a reminder as completed, advancing it if it is recurring."""
        reminder = self.repository.get_by_id(reminder_id)
        if not reminder:
            return

        if reminder.repeat_type and reminder.repeat_type != "None":
            # Move the reminder forward to the next occurrence
            next_date = self.calculate_next_occurrence(reminder.due_date, reminder.repeat_type, reminder.repeat_interval)
            reminder.due_date = next_date
            reminder.completed = False
            self.repository.update(reminder)
        else:
            # Mark as completed
            reminder.completed = True
            self.repository.update(reminder)

    def toggle_reminder_status(self, reminder_id: int) -> None:
        reminder = self.repository.get_by_id(reminder_id)
        if not reminder:
            return

        if reminder.completed:
            reminder.completed = False
            self.repository.update(reminder)
        else:
            self.complete_reminder(reminder_id)

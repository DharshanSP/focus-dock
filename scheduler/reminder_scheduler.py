import time
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from repositories.reminder_repo import ReminderRepository
from models.reminder import Reminder

class ReminderScheduler(QThread):
    # Emits a list of due Reminder objects
    reminder_triggered = pyqtSignal(Reminder)

    def __init__(self, repository: ReminderRepository):
        super().__init__()
        self.repository = repository
        self.running = True
        self.last_checked_minute = None
        self.triggered_ids = set()

    def run(self):
        """Main loop checking for due reminders every 10 seconds to detect minute boundaries."""
        while self.running:
            try:
                now = datetime.now()
                current_minute = now.strftime("%H:%M")
                current_date = now.strftime("%Y-%m-%d")

                # Only trigger check once per minute
                if current_minute != self.last_checked_minute:
                    due_reminders = self.repository.get_pending_active_at(current_date, current_minute)
                    for reminder in due_reminders:
                        if reminder.id not in self.triggered_ids:
                            self.reminder_triggered.emit(reminder)
                            self.triggered_ids.add(reminder.id)
                    
                    # Clean up triggered_ids that are no longer pending or no longer due
                    due_ids = {r.id for r in due_reminders}
                    self.triggered_ids = self.triggered_ids.intersection(due_ids)
                    
                    self.last_checked_minute = current_minute

            except Exception as e:
                print(f"Error in scheduler background task: {e}")

            time.sleep(10)  # Check every 10 seconds to ensure we don't miss a minute transition

    def stop(self):
        self.running = False
        self.wait()

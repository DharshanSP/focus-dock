import unittest
import os
from pathlib import Path
import database.connection
from database.schema import initialize_database
from models.reminder import Reminder
from repositories.reminder_repo import ReminderRepository

class TestReminderRepository(unittest.TestCase):
    def setUp(self):
        # Configure the database path to a test file
        self.test_db_path = Path("test_deskreminder.db")
        database.connection.DB_PATH = self.test_db_path
        
        # Ensure database is clean
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass
                
        # Initialize schema
        initialize_database()
        self.repo = ReminderRepository()

    def tearDown(self):
        # Cleanup test database file
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_create_and_get_reminder(self):
        reminder = Reminder(
            id=None,
            title="Practice Python",
            description="Focus on clean architecture",
            due_date="2026-06-10",
            due_time="15:00",
            priority="High",
            category="Study",
            repeat_type="None"
        )
        reminder_id = self.repo.create(reminder)
        self.assertIsNotNone(reminder_id)

        fetched = self.repo.get_by_id(reminder_id)
        self.assertEqual(fetched.title, "Practice Python")
        self.assertEqual(fetched.priority, "High")
        self.assertFalse(fetched.completed)

if __name__ == "__main__":
    unittest.main()

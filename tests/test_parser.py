import unittest
from services.quick_add_parser import parse_quick_add
from datetime import date, timedelta

class TestQuickAddParser(unittest.TestCase):
    def test_time_parsing(self):
        # 8 PM
        title, due_date, due_time = parse_quick_add("Java practice 8 PM")
        self.assertEqual(title, "Java practice")
        self.assertEqual(due_time, "20:00")

        # 6 AM
        title, due_date, due_time = parse_quick_add("Gym tomorrow 6 AM")
        self.assertEqual(title, "Gym")
        self.assertEqual(due_time, "06:00")

    def test_date_parsing(self):
        # Tomorrow
        title, due_date, due_time = parse_quick_add("Read book tomorrow 10:00")
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(title, "Read book")
        self.assertEqual(due_date, tomorrow_str)

    def test_default_time(self):
        title, due_date, due_time = parse_quick_add("Simple task")
        self.assertEqual(title, "Simple task")
        self.assertEqual(due_time, "12:00")

if __name__ == "__main__":
    unittest.main()

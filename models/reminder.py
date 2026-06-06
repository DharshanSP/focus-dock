from dataclasses import dataclass
from datetime import datetime, date, time

@dataclass
class Reminder:
    id: int | None
    title: str
    description: str
    due_date: str          # YYYY-MM-DD
    due_time: str          # HH:MM
    priority: str          # Low, Medium, High, Critical
    category: str          # Study, Work, Personal, Fitness, Finance, Custom
    repeat_type: str       # None, Daily, Weekly, Monthly, Yearly, Custom
    repeat_interval: int = 1
    completed: bool = False
    is_sticky: bool = False
    sticky_x: int | None = None
    sticky_y: int | None = None
    sticky_width: int = 250
    sticky_height: int = 250
    sticky_theme: str = 'Yellow'
    sticky_pinned: bool = False
    created_at: str | None = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            due_date=row['due_date'],
            due_time=row['due_time'],
            priority=row['priority'],
            category=row['category'],
            repeat_type=row['repeat_type'],
            repeat_interval=row['repeat_interval'],
            completed=bool(row['completed']),
            is_sticky=bool(row['is_sticky']),
            sticky_x=row['sticky_x'],
            sticky_y=row['sticky_y'],
            sticky_width=row['sticky_width'],
            sticky_height=row['sticky_height'],
            sticky_theme=row['sticky_theme'],
            sticky_pinned=bool(row['sticky_pinned']),
            created_at=row['created_at']
        )

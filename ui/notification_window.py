import sys
import winsound
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from models.reminder import Reminder
from services.reminder_service import ReminderService
from repositories.settings_repo import SettingsRepository
from ui.styles import DARK_THEME, LIGHT_THEME, GLASS_THEME

class NotificationWindow(QWidget):
    def __init__(self, reminder: Reminder, service: ReminderService, settings_repo: SettingsRepository, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.reminder = reminder
        self.service = service
        self.settings_repo = settings_repo
        
        self.init_ui()
        self.play_alert_sound()

    def init_ui(self):
        # Semi-transparent/rounded container
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_frame = QWidget(self)
        self.main_frame.setObjectName("mainWidget")
        
        # Apply shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 2)
        self.main_frame.setGraphicsEffect(shadow)
        
        # Apply theme stylesheet
        theme = self.settings_repo.get("theme", "glass")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        elif theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        else:
            self.setStyleSheet(GLASS_THEME)
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("⏰")
        icon_lbl.setStyleSheet("font-size: 20px;")
        
        cat_lbl = QLabel(f"[{self.reminder.category.upper()}]")
        cat_lbl.setStyleSheet("font-weight: bold; color: #0078d4; font-size: 11px;")
        
        priority_colors = {
            "Low": "#a0a0a0", "Medium": "#e0a000",
            "High": "#ff6b6b", "Critical": "#ff0000"
        }
        prio_color = priority_colors.get(self.reminder.priority, "#0078d4")
        prio_lbl = QLabel(f"{self.reminder.priority}")
        prio_lbl.setStyleSheet(f"font-weight: bold; color: {prio_color}; font-size: 11px;")
        
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(cat_lbl)
        header_layout.addStretch()
        header_layout.addWidget(prio_lbl)
        
        # Title & Desc
        title_lbl = QLabel(self.reminder.title)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_lbl.setWordWrap(True)
        
        desc_lbl = QLabel(self.reminder.description or "No description provided.")
        desc_lbl.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        dismiss_btn = QPushButton("Complete")
        dismiss_btn.setObjectName("primaryBtn")
        dismiss_btn.clicked.connect(self.on_complete)
        
        snooze_5 = QPushButton("5m")
        snooze_5.clicked.connect(lambda: self.on_snooze(5))
        
        snooze_10 = QPushButton("10m")
        snooze_10.clicked.connect(lambda: self.on_snooze(10))
        
        snooze_30 = QPushButton("30m")
        snooze_30.clicked.connect(lambda: self.on_snooze(30))
        
        btn_layout.addWidget(dismiss_btn)
        btn_layout.addWidget(snooze_5)
        btn_layout.addWidget(snooze_10)
        btn_layout.addWidget(snooze_30)
        
        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(title_lbl)
        frame_layout.addWidget(desc_lbl)
        frame_layout.addLayout(btn_layout)
        
        layout.addWidget(self.main_frame)
        self.setLayout(layout)
        
        self.resize(320, 180)
        self.position_bottom_right()

    def position_bottom_right(self):
        """Positions the window at the bottom right corner of the screen."""
        from PyQt6.QtWidgets import QApplication
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 20
        self.move(x, y)

    def play_alert_sound(self):
        """Plays the default system alert sound if enabled in settings."""
        if self.settings_repo.get("notification_sound", "true") == "true":
            # Play in background
            winsound.PlaySound("SystemDefault", winsound.SND_ALIAS | winsound.SND_ASYNC)

    def on_complete(self):
        self.service.complete_reminder(self.reminder.id)
        self.close()

    def on_snooze(self, minutes: int):
        # Calculate new due time
        now = datetime.now()
        snoozed_time = now + timedelta(minutes=minutes)
        
        self.reminder.due_date = snoozed_time.strftime("%Y-%m-%d")
        self.reminder.due_time = snoozed_time.strftime("%H:%M")
        self.reminder.completed = False
        
        self.service.repository.update(self.reminder)
        self.close()
        
    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

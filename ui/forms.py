from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QComboBox, QDateEdit, 
                             QTimeEdit, QPushButton, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, QDate, QTime
from models.reminder import Reminder
from repositories.settings_repo import SettingsRepository

class ReminderForm(QDialog):
    def __init__(self, reminder: Reminder | None = None, settings_repo: SettingsRepository = None, parent=None):
        super().__init__(parent)
        self.reminder = reminder
        self.settings_repo = settings_repo
        self.setWindowTitle("Create Reminder" if not reminder else "Edit Reminder")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Style form
        from ui.styles import DARK_THEME, LIGHT_THEME, GLASS_THEME
        theme = self.settings_repo.get("theme", "glass") if self.settings_repo else "glass"
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        elif theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        else:
            self.setStyleSheet(GLASS_THEME)

        # Title
        layout.addWidget(QLabel("Title *"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter reminder title")
        layout.addWidget(self.title_input)

        # Description
        layout.addWidget(QLabel("Description"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter description...")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # Date and Time
        dt_layout = QHBoxLayout()
        date_col = QVBoxLayout()
        date_col.addWidget(QLabel("Due Date"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        date_col.addWidget(self.date_input)
        
        time_col = QVBoxLayout()
        time_col.addWidget(QLabel("Due Time"))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        time_col.addWidget(self.time_input)
        
        dt_layout.addLayout(date_col)
        dt_layout.addLayout(time_col)
        layout.addLayout(dt_layout)

        # Priority and Category
        pc_layout = QHBoxLayout()
        prio_col = QVBoxLayout()
        prio_col.addWidget(QLabel("Priority"))
        self.prio_input = QComboBox()
        self.prio_input.addItems(["Low", "Medium", "High", "Critical"])
        prio_col.addWidget(self.prio_input)
        
        cat_col = QVBoxLayout()
        cat_col.addWidget(QLabel("Category"))
        self.cat_input = QComboBox()
        self.cat_input.addItems(["Personal", "Work", "Study", "Fitness", "Finance", "Custom"])
        cat_col.addWidget(self.cat_input)
        
        pc_layout.addLayout(prio_col)
        pc_layout.addLayout(cat_col)
        layout.addLayout(pc_layout)

        # Repeat Settings
        repeat_layout = QHBoxLayout()
        rep_type_col = QVBoxLayout()
        rep_type_col.addWidget(QLabel("Repeat"))
        self.rep_type_input = QComboBox()
        self.rep_type_input.addItems(["None", "Daily", "Weekly", "Monthly", "Yearly"])
        rep_type_col.addWidget(self.rep_type_input)
        
        rep_int_col = QVBoxLayout()
        rep_int_col.addWidget(QLabel("Interval"))
        self.rep_int_input = QSpinBox()
        self.rep_int_input.setRange(1, 100)
        self.rep_int_input.setValue(1)
        rep_int_col.addWidget(self.rep_int_input)
        
        repeat_layout.addLayout(rep_type_col)
        repeat_layout.addLayout(rep_int_col)
        layout.addLayout(repeat_layout)

        # Sticky Mode
        self.sticky_cb = QCheckBox("Make this a Sticky Note")
        layout.addWidget(self.sticky_cb)
        
        sticky_theme_layout = QHBoxLayout()
        sticky_theme_layout.addWidget(QLabel("Sticky Theme:"))
        self.sticky_theme_input = QComboBox()
        self.sticky_theme_input.addItems(["Yellow", "Blue", "Green", "Pink", "Dark"])
        sticky_theme_layout.addWidget(self.sticky_theme_input)
        layout.addLayout(sticky_theme_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Load data if editing
        if self.reminder:
            self.title_input.setText(self.reminder.title)
            self.desc_input.setText(self.reminder.description)
            self.date_input.setDate(QDate.fromString(self.reminder.due_date, "yyyy-MM-dd"))
            self.time_input.setTime(QTime.fromString(self.reminder.due_time, "HH:mm"))
            self.prio_input.setCurrentText(self.reminder.priority)
            self.cat_input.setCurrentText(self.reminder.category)
            self.rep_type_input.setCurrentText(self.reminder.repeat_type)
            self.rep_int_input.setValue(self.reminder.repeat_interval)
            self.sticky_cb.setChecked(self.reminder.is_sticky)
            self.sticky_theme_input.setCurrentText(self.reminder.sticky_theme)

    def get_reminder_data(self) -> Reminder:
        """Returns a Reminder object populated with form input values."""
        r_id = self.reminder.id if self.reminder else None
        return Reminder(
            id=r_id,
            title=self.title_input.text(),
            description=self.desc_input.toPlainText(),
            due_date=self.date_input.date().toString("yyyy-MM-dd"),
            due_time=self.time_input.time().toString("HH:mm"),
            priority=self.prio_input.currentText(),
            category=self.cat_input.currentText(),
            repeat_type=self.rep_type_input.currentText(),
            repeat_interval=self.rep_int_input.value(),
            completed=self.reminder.completed if self.reminder else False,
            is_sticky=self.sticky_cb.isChecked(),
            sticky_theme=self.sticky_theme_input.currentText(),
            sticky_x=self.reminder.sticky_x if self.reminder else None,
            sticky_y=self.reminder.sticky_y if self.reminder else None,
            sticky_width=self.reminder.sticky_width if self.reminder else 250,
            sticky_height=self.reminder.sticky_height if self.reminder else 250,
            sticky_pinned=self.reminder.sticky_pinned if self.reminder else False
        )


class SettingsWindow(QDialog):
    def __init__(self, settings_repo: SettingsRepository, parent=None):
        super().__init__(parent)
        self.settings_repo = settings_repo
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        from ui.styles import DARK_THEME, LIGHT_THEME, GLASS_THEME
        theme = self.settings_repo.get("theme", "glass")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        elif theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        else:
            self.setStyleSheet(GLASS_THEME)

        # Theme
        layout.addWidget(QLabel("Theme Selection"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "glass"])
        self.theme_combo.setCurrentText(theme)
        layout.addWidget(self.theme_combo)

        # Always-on-top Default
        self.always_on_top_cb = QCheckBox("Always on Top Default")
        self.always_on_top_cb.setChecked(self.settings_repo.get("always_on_top", "false") == "true")
        layout.addWidget(self.always_on_top_cb)

        # Sound Alert
        self.sound_cb = QCheckBox("Enable Notification Sound")
        self.sound_cb.setChecked(self.settings_repo.get("notification_sound", "true") == "true")
        layout.addWidget(self.sound_cb)

        # Windows Startup
        self.startup_cb = QCheckBox("Start with Windows")
        self.startup_cb.setChecked(self.settings_repo.get("startup_with_windows", "false") == "true")
        layout.addWidget(self.startup_cb)

        # Default Duration
        layout.addWidget(QLabel("Default Reminder Duration (minutes)"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)
        self.duration_spin.setValue(int(self.settings_repo.get("default_duration", "30")))
        layout.addWidget(self.duration_spin)

        # Save Button
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def save_settings(self):
        self.settings_repo.set("theme", self.theme_combo.currentText())
        self.settings_repo.set("always_on_top", "true" if self.always_on_top_cb.isChecked() else "false")
        self.settings_repo.set("notification_sound", "true" if self.sound_cb.isChecked() else "false")
        self.settings_repo.set("startup_with_windows", "true" if self.startup_cb.isChecked() else "false")
        self.settings_repo.set("default_duration", str(self.duration_spin.value()))
        self.accept()

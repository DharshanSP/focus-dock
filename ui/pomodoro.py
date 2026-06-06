from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QListWidget)
from PyQt6.QtCore import QTimer, Qt
from repositories.pomodoro_repo import PomodoroRepository
import winsound

class PomodoroTimerView(QWidget):
    def __init__(self, pomodoro_repo: PomodoroRepository, settings_repo, parent=None):
        super().__init__(parent)
        self.pomodoro_repo = pomodoro_repo
        self.settings_repo = settings_repo
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        
        # State variables
        self.mode = "25/5"  # "25/5", "50/10", "Custom"
        self.is_work_session = True
        self.time_left_seconds = 25 * 60
        self.is_running = False

        self.init_ui()
        self.update_timer_display()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header Title
        title = QLabel("Focus Timer")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Mode Selection Buttons
        mode_layout = QHBoxLayout()
        self.btn_25 = QPushButton("25 / 5")
        self.btn_25.clicked.connect(lambda: self.set_preset_mode("25/5", 25))
        
        self.btn_50 = QPushButton("50 / 10")
        self.btn_50.clicked.connect(lambda: self.set_preset_mode("50/10", 50))
        
        self.custom_btn = QPushButton("Custom")
        self.custom_btn.clicked.connect(self.set_custom_mode)
        
        mode_layout.addWidget(self.btn_25)
        mode_layout.addWidget(self.btn_50)
        mode_layout.addWidget(self.custom_btn)
        layout.addLayout(mode_layout)

        # Custom Duration Setup
        self.custom_setup_layout = QHBoxLayout()
        self.custom_setup_layout.addWidget(QLabel("Work (min):"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setValue(25)
        self.custom_setup_layout.addWidget(self.work_spin)
        
        self.custom_setup_layout.addWidget(QLabel("Break (min):"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(5)
        self.custom_setup_layout.addWidget(self.break_spin)
        
        self.set_custom_durations_btn = QPushButton("Set")
        self.set_custom_durations_btn.clicked.connect(self.apply_custom_durations)
        self.custom_setup_layout.addWidget(self.set_custom_durations_btn)
        
        # Hide custom duration inputs by default
        self.custom_container = QWidget()
        self.custom_container.setLayout(self.custom_setup_layout)
        self.custom_container.hide()
        layout.addWidget(self.custom_container)

        # Timer Display
        self.timer_lbl = QLabel("25:00")
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_lbl.setStyleSheet("font-size: 36px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(self.timer_lbl)

        # Status indicator
        self.status_lbl = QLabel("Work Session")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #0078d4; font-weight: 500;")
        layout.addWidget(self.status_lbl)

        # Timer Controls
        ctrl_layout = QHBoxLayout()
        self.start_pause_btn = QPushButton("Start")
        self.start_pause_btn.setObjectName("primaryBtn")
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_timer)
        
        ctrl_layout.addWidget(self.start_pause_btn)
        ctrl_layout.addWidget(self.reset_btn)
        layout.addLayout(ctrl_layout)

        # History list
        layout.addWidget(QLabel("Session History:"))
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(80)
        layout.addWidget(self.history_list)
        
        self.refresh_history()

    def set_preset_mode(self, mode_str, work_mins):
        self.custom_container.hide()
        self.mode = mode_str
        self.is_work_session = True
        self.time_left_seconds = work_mins * 60
        self.status_lbl.setText("Work Session")
        self.status_lbl.setStyleSheet("color: #0078d4; font-weight: 500;")
        self.stop_timer()
        self.update_timer_display()

    def set_custom_mode(self):
        self.custom_container.show()
        self.mode = "Custom"

    def apply_custom_durations(self):
        self.is_work_session = True
        self.time_left_seconds = self.work_spin.value() * 60
        self.status_lbl.setText("Work Session")
        self.status_lbl.setStyleSheet("color: #0078d4; font-weight: 500;")
        self.stop_timer()
        self.update_timer_display()

    def toggle_timer(self):
        if self.is_running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.start_pause_btn.setText("Pause")
        self.timer.start(1000)

    def stop_timer(self):
        self.is_running = False
        self.start_pause_btn.setText("Start")
        self.timer.stop()

    def reset_timer(self):
        self.stop_timer()
        if self.mode == "25/5":
            self.time_left_seconds = 25 * 60
        elif self.mode == "50/10":
            self.time_left_seconds = 50 * 60
        else:
            self.time_left_seconds = self.work_spin.value() * 60
        self.is_work_session = True
        self.status_lbl.setText("Work Session")
        self.status_lbl.setStyleSheet("color: #0078d4; font-weight: 500;")
        self.update_timer_display()

    def tick(self):
        if self.time_left_seconds > 0:
            self.time_left_seconds -= 1
            self.update_timer_display()
        else:
            self.on_session_complete()

    def update_timer_display(self):
        mins = self.time_left_seconds // 60
        secs = self.time_left_seconds % 60
        self.timer_lbl.setText(f"{mins:02d}:{secs:02d}")

    def on_session_complete(self):
        self.stop_timer()
        
        # Play alert sound
        if self.settings_repo.get("notification_sound", "true") == "true":
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)

        if self.is_work_session:
            # Completed work session! Save to DB
            duration = 25 * 60 if self.mode == "25/5" else (50 * 60 if self.mode == "50/10" else self.work_spin.value() * 60)
            self.pomodoro_repo.create_session(self.mode, duration)
            self.refresh_history()
            
            # Switch to Break
            self.is_work_session = False
            self.status_lbl.setText("Break Time! Relax ☕")
            self.status_lbl.setStyleSheet("color: #2e7d32; font-weight: 500;")
            
            if self.mode == "25/5":
                self.time_left_seconds = 5 * 60
            elif self.mode == "50/10":
                self.time_left_seconds = 10 * 60
            else:
                self.time_left_seconds = self.break_spin.value() * 60
        else:
            # Break complete, switch back to Work
            self.is_work_session = True
            self.status_lbl.setText("Back to Work! 🎯")
            self.status_lbl.setStyleSheet("color: #0078d4; font-weight: 500;")
            
            if self.mode == "25/5":
                self.time_left_seconds = 25 * 60
            elif self.mode == "50/10":
                self.time_left_seconds = 50 * 60
            else:
                self.time_left_seconds = self.work_spin.value() * 60

        self.update_timer_display()

    def refresh_history(self):
        self.history_list.clear()
        sessions = self.pomodoro_repo.get_history(5)
        for s in sessions:
            completed_time = s['completed_at'].split(" ")[1][:5] if " " in s['completed_at'] else s['completed_at']
            duration_mins = s['duration'] // 60
            self.history_list.addItem(f"[{s['mode']}] {duration_mins} mins - {completed_time}")

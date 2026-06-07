import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QCheckBox, 
                             QScrollArea, QFrame, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QPoint, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen
from models.reminder import Reminder
from repositories.reminder_repo import ReminderRepository
from repositories.settings_repo import SettingsRepository
from repositories.pomodoro_repo import PomodoroRepository
from services.reminder_service import ReminderService
from services.quick_add_parser import parse_quick_add
from ui.forms import ReminderForm, SettingsWindow
from ui.sticky import StickyNoteWindow
from ui.pomodoro import PomodoroTimerView
from ui.styles import DARK_THEME, LIGHT_THEME, GLASS_THEME

class ReminderCard(QFrame):
    def __init__(self, reminder: Reminder, service: ReminderService, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.reminder = reminder
        self.service = service
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.init_ui()

    def init_ui(self):
        self.setObjectName("reminderCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Determine priority color
        priority_colors = {
            "Low": "#888888", "Medium": "#ffb300",
            "High": "#ff5555", "Critical": "#d50000"
        }
        prio_color = priority_colors.get(self.reminder.priority, "#0078d4")
        
        self.setStyleSheet(f"""
            QFrame#reminderCard {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 4px solid {prio_color};
                border-radius: 6px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Checkbox
        self.cb = QCheckBox()
        self.cb.setChecked(self.reminder.completed)
        self.cb.stateChanged.connect(self.on_checked_changed)
        layout.addWidget(self.cb)

        # Info Layout (Title & Date/Time/Category)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Strikethrough for completed reminders
        self.title_lbl = QLabel(self.reminder.title)
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.meta_lbl = QLabel(f"⏰ {self.reminder.due_date} {self.reminder.due_time} | [{self.reminder.category}]")
        self.meta_lbl.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.5);")

        if self.reminder.completed:
            self.title_lbl.setStyleSheet("text-decoration: line-through; color: rgba(255, 255, 255, 0.4);")
            self.meta_lbl.setStyleSheet("font-size: 11px; text-decoration: line-through; color: rgba(255, 255, 255, 0.3);")
        else:
            self.title_lbl.setStyleSheet("font-weight: 500;")

        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.meta_lbl)
        layout.addLayout(info_layout, 1)

        # Edit and Delete buttons
        self.edit_btn = QPushButton()
        self.edit_btn.setFixedSize(14, 14)
        self.edit_btn.setStyleSheet("background-color: #4caf50; border: none; border-radius: 7px;")
        self.edit_btn.setToolTip("Edit Reminder")
        self.edit_btn.clicked.connect(lambda: self.on_edit(self.reminder))
        
        self.delete_btn = QPushButton()
        self.delete_btn.setFixedSize(14, 14)
        self.delete_btn.setStyleSheet("background-color: #f44336; border: none; border-radius: 7px;")
        self.delete_btn.setToolTip("Delete Reminder")
        self.delete_btn.clicked.connect(lambda: self.on_delete(self.reminder.id))

        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)

    def on_checked_changed(self, state):
        self.service.toggle_reminder_status(self.reminder.id)
        # Re-fetch state
        self.reminder = self.service.repository.get_by_id(self.reminder.id)
        
        # Traverse up tree to find DeskReminderWidget and trigger list refresh
        parent_widget = self.parent()
        while parent_widget:
            if hasattr(parent_widget, 'refresh_reminder_list'):
                parent_widget.refresh_reminder_list()
                break
            parent_widget = parent_widget.parent()
        else:
            self.init_ui()


class DeskReminderWidget(QWidget):
    def __init__(self, reminder_repo: ReminderRepository, settings_repo: SettingsRepository, pomodoro_repo: PomodoroRepository):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.reminder_repo = reminder_repo
        self.settings_repo = settings_repo
        self.pomodoro_repo = pomodoro_repo
        self.reminder_service = ReminderService(reminder_repo)
        
        self.is_expanded = True
        self.always_on_top = self.settings_repo.get("always_on_top", "false") == "true"
        self.drag_position = QPoint()
        self.open_stickies = {}  # reminder_id -> StickyNoteWindow
        
        self.init_ui()
        self.setMouseTracking(True)
        self.frame.setMouseTracking(True)
        self.apply_theme()
        self.refresh_reminder_list()
        self.restore_window_position()
        self.open_active_stickies()

    def init_ui(self):
        # Frameless rounded glass window setup
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("mainWidget")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Inner container representing the glass frame
        self.frame = QFrame()
        self.frame.setObjectName("mainWidget")
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(15, 15, 15, 15)
        self.frame_layout.setSpacing(10)
        self.main_layout.addWidget(self.frame)

        # ---------------- COLLAPSED VIEW ----------------
        self.collapsed_widget = QWidget()
        collapsed_layout = QHBoxLayout(self.collapsed_widget)
        collapsed_layout.setContentsMargins(0, 0, 0, 0)
        
        self.collapsed_btn = QPushButton("⏰ 0")
        self.collapsed_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.collapsed_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 212, 0.85);
                color: white;
                border-radius: 20px;
                padding: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:hover {
                background-color: rgba(16, 110, 190, 0.95);
            }
        """)
        self.collapsed_btn.setFixedSize(80, 40)
        self.collapsed_btn.clicked.connect(self.expand_widget)
        collapsed_layout.addWidget(self.collapsed_btn)
        self.frame_layout.addWidget(self.collapsed_widget)
        self.collapsed_widget.hide()  # Start expanded

        # ---------------- EXPANDED VIEW ----------------
        self.expanded_widget = QWidget()
        self.expanded_layout = QVBoxLayout(self.expanded_widget)
        self.expanded_layout.setContentsMargins(0, 0, 0, 0)
        self.expanded_layout.setSpacing(10)

        # Header Section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(20, 20)
        self.help_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.help_btn.setToolTip("User Guide & Shortcuts")
        self.help_btn.clicked.connect(self.show_user_guide)
        
        self.title_lbl = QLabel("DeskReminder")
        self.title_lbl.setObjectName("title")
        
        self.pin_btn = QPushButton()
        self.pin_btn.setFixedSize(14, 14)
        self.pin_btn.setStyleSheet("background-color: #00bcd4; border: none; border-radius: 7px;")
        self.pin_btn.setToolTip("Toggle Always on Top")
        self.pin_btn.clicked.connect(self.toggle_always_on_top)
        
        collapse_btn = QPushButton()
        collapse_btn.setFixedSize(14, 14)
        collapse_btn.setStyleSheet("background-color: #ff9800; border: none; border-radius: 7px;")
        collapse_btn.setToolTip("Minimize Widget")
        collapse_btn.clicked.connect(self.collapse_widget)

        settings_btn = QPushButton()
        settings_btn.setFixedSize(14, 14)
        settings_btn.setStyleSheet("background-color: #9c27b0; border: none; border-radius: 7px;")
        settings_btn.setToolTip("Open Settings")
        settings_btn.clicked.connect(self.open_settings_dialog)

        close_btn = QPushButton()
        close_btn.setFixedSize(14, 14)
        close_btn.setStyleSheet("background-color: #e53935; border: none; border-radius: 7px;")
        close_btn.setToolTip("Exit Application")
        close_btn.clicked.connect(self.exit_app)

        header_layout.addWidget(self.help_btn)
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_btn)
        header_layout.addWidget(collapse_btn)
        header_layout.addWidget(settings_btn)
        header_layout.addWidget(close_btn)
        self.expanded_layout.addLayout(header_layout)

        # Stats / Dashboard (Inline)
        self.stats_layout = QHBoxLayout()
        self.stat_today_lbl = QLabel("Today: 0")
        self.stat_today_lbl.setStyleSheet("font-size: 11px; font-weight: 500;")
        self.stat_pending_lbl = QLabel("Pending: 0")
        self.stat_pending_lbl.setStyleSheet("font-size: 11px; font-weight: 500;")
        self.stat_completion_lbl = QLabel("Done: 0%")
        self.stat_completion_lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: #4caf50;")
        
        self.stats_layout.addWidget(self.stat_today_lbl)
        self.stats_layout.addWidget(self.stat_pending_lbl)
        self.stats_layout.addWidget(self.stat_completion_lbl)
        self.expanded_layout.addLayout(self.stats_layout)

        # Quick Add Field
        self.quick_add_input = QLineEdit()
        self.quick_add_input.setPlaceholderText("e.g. Gym tomorrow 6 AM (Enter)")
        self.quick_add_input.returnPressed.connect(self.on_quick_add)
        self.expanded_layout.addWidget(self.quick_add_input)

        # Search, Filter, Sort Controls
        controls_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.refresh_reminder_list)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Today", "Upcoming", "Completed", "High Priority"])
        self.filter_combo.currentTextChanged.connect(self.refresh_reminder_list)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Time", "Priority", "Date Created", "Alphabetical"])
        self.sort_combo.currentTextChanged.connect(self.refresh_reminder_list)

        controls_layout.addWidget(self.search_input, 2)
        controls_layout.addWidget(self.filter_combo, 1)
        controls_layout.addWidget(self.sort_combo, 1)
        self.expanded_layout.addLayout(controls_layout)

        # Scrollable Reminder List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.addStretch()  # pushes everything up
        self.scroll_area.setWidget(self.scroll_content)
        self.expanded_layout.addWidget(self.scroll_area, 1)

        # Main Actions (Add standard reminder, Open Focus timer)
        actions_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Standard")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self.open_add_dialog)
        
        self.pomodoro_btn = QPushButton("⏱️ Focus Timer")
        self.pomodoro_btn.clicked.connect(self.toggle_pomodoro_view)
        
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(self.pomodoro_btn)
        self.expanded_layout.addLayout(actions_layout)

        # Embedded Pomodoro View (Toggled on demand)
        self.pomodoro_view = PomodoroTimerView(self.pomodoro_repo, self.settings_repo)
        self.pomodoro_view.hide()
        self.expanded_layout.addWidget(self.pomodoro_view)

        self.frame_layout.addWidget(self.expanded_widget)

        self.resize(360, 500)

    def apply_theme(self):
        theme = self.settings_repo.get("theme", "glass")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        elif theme == "light":
            self.setStyleSheet(LIGHT_THEME)
        else:
            self.setStyleSheet(GLASS_THEME)

    def show_and_activate(self):
        self.show()
        self.activateWindow()

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        # Text label removed to keep colors-only minimal interface
        
        # Reset window flags
        pos = self.pos()
        size = self.size()
        flags = Qt.WindowType.FramelessWindowHint
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.move(pos)
        self.resize(size)
        self.show()

    def collapse_widget(self):
        self.is_expanded = False
        self.expanded_widget.hide()
        self.collapsed_widget.show()
        # Resize dynamically with animation
        self.animate_resize(100, 60)

    def expand_widget(self):
        self.is_expanded = True
        self.collapsed_widget.hide()
        self.expanded_widget.show()
        self.animate_resize(360, 500)

    def animate_resize(self, width, height):
        self.anim = QPropertyAnimation(self, b"size")
        self.anim.setDuration(150)
        self.anim.setEndValue(QSize(width, height))
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

    def on_quick_add(self):
        text = self.quick_add_input.text().strip()
        if not text:
            return
            
        title, due_date, due_time = parse_quick_add(text)
        
        # Create default categories and priority
        reminder = Reminder(
            id=None,
            title=title,
            description="",
            due_date=due_date,
            due_time=due_time,
            priority="Medium",
            category="Personal",
            repeat_type="None"
        )
        self.reminder_repo.create(reminder)
        self.quick_add_input.clear()
        self.refresh_reminder_list()

    def refresh_reminder_list(self):
        # Clear previous cards (keeping the bottom stretch)
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        search = self.search_input.text()
        filter_by = self.filter_combo.currentText()
        sort_by = self.sort_combo.currentText()

        # Fetch matching reminders
        reminders = self.reminder_repo.get_all(search=search, filter_by=filter_by, sort_by=sort_by)
        
        # Populate layout
        for reminder in reminders:
            card = ReminderCard(reminder, self.reminder_service, self.open_edit_dialog, self.delete_reminder, self)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        # Update stats
        all_reminders = self.reminder_repo.get_all()
        pending_count = len([r for r in all_reminders if not r.completed])
        completed_count = len([r for r in all_reminders if r.completed])
        
        today_str = QPoint().x()  # dummy
        import datetime
        today_date_str = datetime.date.today().strftime("%Y-%m-%d")
        today_reminders = [r for r in all_reminders if r.due_date == today_date_str]
        
        self.stat_today_lbl.setText(f"Today: {len(today_reminders)}")
        self.stat_pending_lbl.setText(f"Pending: {pending_count}")
        
        total = pending_count + completed_count
        percent = int((completed_count / total) * 100) if total > 0 else 0
        self.stat_completion_lbl.setText(f"Done: {percent}%")
        
        self.collapsed_btn.setText(f"⏰ {pending_count}")

    def open_add_dialog(self):
        dialog = ReminderForm(reminder=None, settings_repo=self.settings_repo, parent=self)
        if dialog.exec():
            reminder_data = dialog.get_reminder_data()
            reminder_id = self.reminder_repo.create(reminder_data)
            reminder_data.id = reminder_id
            
            # Handle launching sticky note immediately if checked
            if reminder_data.is_sticky:
                self.launch_sticky_note(reminder_data)
                
            self.refresh_reminder_list()

    def open_edit_dialog(self, reminder: Reminder):
        dialog = ReminderForm(reminder=reminder, settings_repo=self.settings_repo, parent=self)
        if dialog.exec():
            updated_data = dialog.get_reminder_data()
            self.reminder_repo.update(updated_data)
            
            # Handle sticky window transitions
            if updated_data.is_sticky:
                self.launch_sticky_note(updated_data)
            else:
                self.close_sticky_note(updated_data.id)
                
            self.refresh_reminder_list()

    def delete_reminder(self, reminder_id: int):
        self.reminder_repo.delete(reminder_id)
        self.close_sticky_note(reminder_id)
        self.refresh_reminder_list()

    def toggle_pomodoro_view(self):
        if self.pomodoro_view.isVisible():
            self.pomodoro_view.hide()
            self.pomodoro_btn.setText("⏱️ Focus Timer")
            self.animate_resize(360, 500)
        else:
            self.pomodoro_view.show()
            self.pomodoro_btn.setText("▲ Hide Timer")
            self.animate_resize(360, 620)

    def open_settings_dialog(self):
        dialog = SettingsWindow(self.settings_repo, parent=self)
        if dialog.exec():
            self.apply_theme()
            self.refresh_reminder_list()

    def show_user_guide(self):
        from PyQt6.QtWidgets import QMessageBox
        guide_text = (
            "<h3>DeskReminder Guide</h3>"
            "<p><b>Color-Coded Buttons:</b></p>"
            "<ul>"
            "<li><span style='color:#00bcd4;'>● Cyan</span>: Toggle Always on Top (Pin)</li>"
            "<li><span style='color:#ff9800;'>● Orange</span>: Minimize window</li>"
            "<li><span style='color:#9c27b0;'>● Purple</span>: Settings dialog</li>"
            "<li><span style='color:#e53935;'>● Dark Red</span>: Exit / Close app</li>"
            "<li><span style='color:#4caf50;'>● Green</span>: Edit reminder</li>"
            "<li><span style='color:#f44336;'>● Red</span>: Delete reminder</li>"
            "</ul>"
            "<p><b>Keyboard Shortcuts:</b></p>"
            "<ul>"
            "<li><b>Ctrl + N</b>: New Reminder</li>"
            "<li><b>Ctrl + F</b>: Search Bar</li>"
            "<li><b>Ctrl + D</b>: Cycle Themes</li>"
            "</ul>"
            "<p><b>Resizing:</b> Drag borders or bottom-right corner to resize window.</p>"
        )
        QMessageBox.information(self, "DeskReminder User Guide", guide_text)

    # Sticky Note triggers
    def launch_sticky_note(self, reminder: Reminder):
        self.close_sticky_note(reminder.id)  # close existing if open
        sticky = StickyNoteWindow(reminder, self.reminder_repo, on_close_cb=self.close_sticky_note)
        self.open_stickies[reminder.id] = sticky
        sticky.show()

    def close_sticky_note(self, reminder_id: int):
        if reminder_id in self.open_stickies:
            self.open_stickies[reminder_id].close()
            del self.open_stickies[reminder_id]

    def open_active_stickies(self):
        stickies = self.reminder_repo.get_sticky_notes()
        for s in stickies:
            self.launch_sticky_note(s)

    def exit_app(self):
        # Close all open sticky notes
        for s in list(self.open_stickies.values()):
            s.close()
        sys.exit(0)

    # Window position persistence
    def restore_window_position(self):
        from PyQt6.QtWidgets import QApplication
        geometry = QApplication.primaryScreen().geometry()
        # Default position: Right edge center
        x = geometry.width() - self.width() - 40
        y = (geometry.height() - self.height()) // 2
        
        saved_x = self.settings_repo.get("window_x")
        saved_y = self.settings_repo.get("window_y")
        if saved_x and saved_y:
            self.move(int(saved_x), int(saved_y))
        else:
            self.move(x, y)

    def closeEvent(self, event):
        # Override close event to minimize to tray instead
        event.ignore()
        self.hide()

    # Dragging & Resizing logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            self.resize_direction = None
            margin = 12
            rect = self.rect()
            
            if pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
                self.resize_direction = "both"
            elif pos.x() >= rect.width() - margin:
                self.resize_direction = "horizontal"
            elif pos.y() >= rect.height() - margin:
                self.resize_direction = "vertical"
            else:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.NoButton:
            pos = event.position()
            margin = 12
            rect = self.rect()
            if pos.x() >= rect.width() - margin and pos.y() >= rect.height() - margin:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif pos.x() >= rect.width() - margin:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif pos.y() >= rect.height() - margin:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if event.buttons() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'resize_direction') and self.resize_direction:
                delta_x = event.globalPosition().toPoint().x() - self.x()
                delta_y = event.globalPosition().toPoint().y() - self.y()
                new_w = max(300, delta_x)
                new_h = max(200, delta_y)
                
                if self.resize_direction == "horizontal":
                    self.resize(new_w, self.height())
                elif self.resize_direction == "vertical":
                    self.resize(self.width(), new_h)
                elif self.resize_direction == "both":
                    self.resize(new_w, new_h)
            else:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                self.settings_repo.set("window_x", str(self.x()))
                self.settings_repo.set("window_y", str(self.y()))
            event.accept()

    def mouseReleaseEvent(self, event):
        self.resize_direction = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

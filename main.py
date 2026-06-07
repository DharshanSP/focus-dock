import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from database.schema import initialize_database
from repositories.reminder_repo import ReminderRepository
from repositories.settings_repo import SettingsRepository
from repositories.pomodoro_repo import PomodoroRepository
from scheduler.reminder_scheduler import ReminderScheduler
from ui.widget import DeskReminderWidget
from ui.notification_window import NotificationWindow
from tray.system_tray import DeskReminderSystemTray
from utils.shortcuts import setup_keyboard_shortcuts

class DeskReminderApp:
    def __init__(self):
        # 1. Initialize SQLite Database
        initialize_database()
        
        # 2. Setup repositories
        self.reminder_repo = ReminderRepository()
        self.settings_repo = SettingsRepository()
        self.pomodoro_repo = PomodoroRepository()
        
        # 3. Create the Main Window widget
        self.widget = DeskReminderWidget(
            self.reminder_repo,
            self.settings_repo,
            self.pomodoro_repo
        )
        
        # 4. Setup keyboard shortcuts
        setup_keyboard_shortcuts(self.widget)
        
        # 5. Setup System Tray
        self.tray = DeskReminderSystemTray(self.widget)
        self.tray.show()
        
        # 6. Initialize & Start the background scheduler
        self.scheduler = ReminderScheduler(self.reminder_repo)
        self.scheduler.reminder_triggered.connect(self.on_reminder_due)
        self.scheduler.start()
        
        # Store active notifications to prevent garbage collection
        self.active_notifications = []

    def on_reminder_due(self, reminder):
        """Callback when background scheduler detects a due reminder."""
        # Create and display notification popup
        popup = NotificationWindow(
            reminder,
            self.widget.reminder_service,
            self.settings_repo
        )
        
        # Clean up closed notifications from memory
        popup.destroyed.connect(lambda: self.active_notifications.remove(popup))
        self.active_notifications.append(popup)
        
        # Also trigger native system tray notification popup if tray is available
        self.tray.showMessage(
            f"Reminder: {reminder.title}",
            reminder.description or "No description",
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )
        
        popup.show()
        popup.raise_()
        popup.activateWindow()
        
        # Show and activate the main app window
        self.widget.show_and_activate()
        if not self.widget.is_expanded:
            self.widget.expand_widget()
        
        # Refresh the main list UI to reflect any changes if needed
        self.widget.refresh_reminder_list()

    def run(self):
        # Default behavior: Show main widget on startup
        self.widget.show_and_activate()
        
        # Cleanup scheduler on exit
        app_exit_code = app.exec()
        self.scheduler.stop()
        sys.exit(app_exit_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ensure application does not quit when the main window is hidden
    app.setQuitOnLastWindowClosed(False)
    
    reminder_app = DeskReminderApp()
    reminder_app.run()

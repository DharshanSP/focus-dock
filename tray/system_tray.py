from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject

class DeskReminderSystemTray(QSystemTrayIcon):
    def __init__(self, main_window, parent=None):
        # We can use a standard system icon or a unicode clock emoji as character-based fallback icon
        # To make it super robust on any platform, let's create a small fallback icon using QIcon or standard graphics
        # Actually, QIcon.fromTheme("appointment-new") or a simple pixel map is very safe.
        # Let's generate a basic icon, or check if we can use a built-in icon format.
        # Drawing a simple blue circle with a clock hands using QPixmap is a great way to guarantee a beautiful icon!
        from PyQt6.QtGui import QPixmap, QPainter, QColor
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#0078d4"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⏰")
        painter.end()
        icon = QIcon(pixmap)

        super().__init__(icon, parent)
        self.main_window = main_window
        self.setToolTip("DeskReminder")
        
        self.init_menu()
        self.activated.connect(self.on_activated)

    def init_menu(self):
        menu = QMenu()
        
        open_action = QAction("Open DeskReminder", self)
        open_action.triggered.connect(self.main_window.show_and_activate)
        
        add_action = QAction("Add Reminder", self)
        add_action.triggered.connect(self.main_window.open_add_dialog)
        
        always_on_top_action = QAction("Toggle Always On Top", self)
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.main_window.always_on_top)
        always_on_top_action.triggered.connect(self.main_window.toggle_always_on_top)
        self.always_on_top_action = always_on_top_action
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.main_window.open_settings_dialog)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.main_window.exit_app)
        
        menu.addAction(open_action)
        menu.addAction(add_action)
        menu.addAction(always_on_top_action)
        menu.addSeparator()
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.main_window.show_and_activate()

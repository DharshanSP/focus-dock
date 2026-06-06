from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QComboBox, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QFont
from models.reminder import Reminder
from repositories.reminder_repo import ReminderRepository
from ui.styles import STICKY_THEMES

class StickyNoteWindow(QWidget):
    def __init__(self, reminder: Reminder, repository: ReminderRepository, on_close_cb=None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.reminder = reminder
        self.repository = repository
        self.on_close_cb = on_close_cb
        
        self.pinned = self.reminder.sticky_pinned
        self.drag_position = QPoint()

        self.init_ui()
        self.apply_theme()
        self.restore_geometry()
        self.update_always_on_top()

    def init_ui(self):
        # Allow borderless window with drop shadow
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_container = QWidget(self)
        self.main_container.setObjectName("stickyContainer")
        
        # Apply shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(10, 5, 10, 10)
        container_layout.setSpacing(5)

        # Header Bar (Control Bar)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)

        # Color changer
        self.color_selector = QComboBox()
        self.color_selector.addItems(["Yellow", "Blue", "Green", "Pink", "Dark"])
        self.color_selector.setCurrentText(self.reminder.sticky_theme)
        self.color_selector.currentTextChanged.connect(self.on_theme_changed)
        self.color_selector.setFixedWidth(75)
        self.color_selector.setStyleSheet("""
            QComboBox { 
                background: transparent; 
                border: 1px solid rgba(0, 0, 0, 0.1); 
                border-radius: 3px; 
                font-size: 11px;
                padding-left: 3px;
            }
            QComboBox::drop-down { border: none; }
        """)

        # Pinned state toggle
        self.pin_btn = QPushButton("📌" if self.pinned else "📍")
        self.pin_btn.setToolTip("Toggle Always on Top")
        self.pin_btn.setFixedSize(22, 22)
        self.pin_btn.clicked.connect(self.toggle_pin)

        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setToolTip("Close Sticky Note")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.clicked.connect(self.close_sticky)

        header_layout.addWidget(self.color_selector)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_btn)
        header_layout.addWidget(self.close_btn)

        # Editable Title
        self.title_edit = QLineEdit(self.reminder.title)
        self.title_edit.setPlaceholderText("Title")
        self.title_edit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_edit.textChanged.connect(self.auto_save)
        self.title_edit.setStyleSheet("background: transparent; border: none; font-weight: bold; padding: 2px;")

        # Editable Content
        self.content_edit = QTextEdit(self.reminder.description or "")
        self.content_edit.setPlaceholderText("Take a note...")
        self.content_edit.setFont(QFont("Segoe UI", 10))
        self.content_edit.textChanged.connect(self.auto_save)
        self.content_edit.setStyleSheet("background: transparent; border: none; padding: 2px;")

        container_layout.addLayout(header_layout)
        container_layout.addWidget(self.title_edit)
        container_layout.addWidget(self.content_edit)
        
        layout.addWidget(self.main_container)
        self.setLayout(layout)

        # Apply basic button styling
        self.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                border: none; 
                font-size: 12px; 
                border-radius: 4px;
            }
        """)
        
        self.resize(self.reminder.sticky_width, self.reminder.sticky_height)

    def apply_theme(self):
        theme_name = self.color_selector.currentText()
        colors = STICKY_THEMES.get(theme_name, STICKY_THEMES["Yellow"])
        
        bg = colors["bg"]
        txt = colors["text"]
        border = colors["border"]
        btn_hover = colors["btn_hover"]
        
        self.main_container.setStyleSheet(f"""
            QWidget#stickyContainer {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QLineEdit, QTextEdit, QLabel, QComboBox {{
                color: {txt};
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)

    def on_theme_changed(self, new_theme):
        self.reminder.sticky_theme = new_theme
        self.apply_theme()
        self.auto_save()

    def toggle_pin(self):
        self.pinned = not self.pinned
        self.reminder.sticky_pinned = self.pinned
        self.pin_btn.setText("📌" if self.pinned else "📍")
        self.update_always_on_top()
        self.auto_save()

    def update_always_on_top(self):
        # Re-set window flags to toggle stays-on-top
        pos = self.pos()
        size = self.size()
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow
        if self.pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.move(pos)
        self.resize(size)
        self.show()

    def auto_save(self):
        self.reminder.title = self.title_edit.text()
        self.reminder.description = self.content_edit.toPlainText()
        self.reminder.sticky_width = self.width()
        self.reminder.sticky_height = self.height()
        self.reminder.sticky_x = self.x()
        self.reminder.sticky_y = self.y()
        self.repository.update(self.reminder)

    def restore_geometry(self):
        if self.reminder.sticky_x is not None and self.reminder.sticky_y is not None:
            self.move(self.reminder.sticky_x, self.reminder.sticky_y)

    def close_sticky(self):
        self.reminder.is_sticky = False
        self.repository.update(self.reminder)
        if self.on_close_cb:
            self.on_close_cb(self.reminder.id)
        self.close()

    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.auto_save()
            event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Save dimension changes
        self.auto_save()

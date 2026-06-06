# Stylesheets for DeskReminder themes: Dark, Light, Glassmorphic

DARK_THEME = """
QWidget {
    background-color: #1a1a1a;
    color: #f0f0f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#mainWidget {
    background-color: #242424;
    border: 1px solid #333333;
    border-radius: 12px;
}
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f0f0f0;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #505050;
}
QPushButton:pressed {
    background-color: #1e1e1e;
}
QPushButton#primaryBtn {
    background-color: #0078d4;
    border: none;
    color: white;
}
QPushButton#primaryBtn:hover {
    background-color: #106ebe;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
    background-color: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 6px;
    color: #f0f0f0;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid #0078d4;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #505050;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}
QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#statNum {
    font-size: 24px;
    font-weight: bold;
    color: #0078d4;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #1a1a1a;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #404040;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #505050;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f3f3f3;
    color: #333333;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#mainWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 6px 12px;
    color: #333333;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f9f9f9;
    border-color: #bbbbbb;
}
QPushButton:pressed {
    background-color: #eaeaea;
}
QPushButton#primaryBtn {
    background-color: #0078d4;
    border: none;
    color: white;
}
QPushButton#primaryBtn:hover {
    background-color: #106ebe;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 6px;
    color: #333333;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid #0078d4;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #cccccc;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}
QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #111111;
}
QLabel#statNum {
    font-size: 24px;
    font-weight: bold;
    color: #0078d4;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #f3f3f3;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #cccccc;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #bbbbbb;
}
"""

GLASS_THEME = """
QWidget {
    background-color: transparent;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#mainWidget {
    background-color: rgb(30, 30, 30);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}
QPushButton {
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
}
QPushButton:pressed {
    background-color: rgba(0, 0, 0, 0.3);
}
QPushButton#primaryBtn {
    background-color: rgba(0, 120, 212, 0.8);
    border: none;
    color: white;
}
QPushButton#primaryBtn:hover {
    background-color: rgba(16, 110, 190, 0.9);
}
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
    background-color: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 6px;
    color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid rgba(0, 120, 212, 0.8);
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}
QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#statNum {
    font-size: 24px;
    font-weight: bold;
    color: #00f0ff;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.4);
}
"""

STICKY_THEMES = {
    "Yellow": {
        "bg": "#fef5c8", "text": "#4f3711", "border": "#edd471", "btn_hover": "#ede4b1"
    },
    "Blue": {
        "bg": "#d8f0fd", "text": "#113854", "border": "#8fcdec", "btn_hover": "#cde8f9"
    },
    "Green": {
        "bg": "#dcfbe3", "text": "#164421", "border": "#9ee1ad", "btn_hover": "#cdf4d6"
    },
    "Pink": {
        "bg": "#ffdfeb", "text": "#54162e", "border": "#ecabcc", "btn_hover": "#fcd0e2"
    },
    "Dark": {
        "bg": "#333333", "text": "#f0f0f0", "border": "#444444", "btn_hover": "#4f4f4f"
    }
}

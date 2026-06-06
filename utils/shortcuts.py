from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

def setup_keyboard_shortcuts(window):
    """Registers global/local keyboard shortcuts for the DeskReminder widget."""
    # Ctrl + N: Open Add Reminder standard form
    shortcut_new = QShortcut(QKeySequence("Ctrl+N"), window)
    shortcut_new.activated.connect(window.open_add_dialog)

    # Ctrl + F: Focus the Search box
    shortcut_search = QShortcut(QKeySequence("Ctrl+F"), window)
    shortcut_search.activated.connect(lambda: window.search_input.setFocus())

    # Ctrl + D: Toggle theme
    shortcut_theme = QShortcut(QKeySequence("Ctrl+D"), window)
    shortcut_theme.activated.connect(lambda: toggle_theme_shortcut(window))

def toggle_theme_shortcut(window):
    current_theme = window.settings_repo.get("theme", "glass")
    next_themes = {"glass": "dark", "dark": "light", "light": "glass"}
    next_theme = next_themes.get(current_theme, "glass")
    
    window.settings_repo.set("theme", next_theme)
    window.apply_theme()

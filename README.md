# DeskReminder

A lightweight, offline-first desktop reminder widget designed for personal productivity. It is a modern combination of Windows Sticky Notes, Microsoft To Do, and a desktop widget.

## Features

- **Frameless Floating Widget**: Draggable, resizable, always-on-top toggle, and smooth collapse/expand states.
- **Natural Language Parsing**: Quick-add reminders like "Java practice 8 PM", "Gym tomorrow 6 AM", or "Submit assignment Friday" parsed instantly.
- **Sticky Note Mode**: Convert any reminder into a floating, editable stick note with multiple themes (Yellow, Blue, Green, Pink, Dark).
- **Pomodoro Focus Timer**: Customizable Pomodoro timer (25/5, 50/10, Custom) with notification alerts and session history.
- **Local SQLite Database**: Fully offline database structure using DAO and Repository pattern.
- **System Tray Integration**: Minimize to tray with status options, quick add, and settings access.
- **Glassmorphic UI**: Beautiful glassmorphism, responsive animations, and dark/light themes.

## Tech Stack

- **Python 3.14**
- **PyQt6** (Desktop GUI Framework)
- **SQLite** (Local Database)

## Setup & Running

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the application:
   ```bash
   python main.py
   ```

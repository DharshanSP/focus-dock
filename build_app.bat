@echo off
cd /d "%~dp0"
echo Building DeskReminder executable...
pyinstaller --onefile --windowed main.py
if %errorlevel% neq 0 (
    echo PyInstaller failed. Ensure it is installed (pip install pyinstaller).
) else (
    echo Build complete. Executable is in the dist folder.
)
pause

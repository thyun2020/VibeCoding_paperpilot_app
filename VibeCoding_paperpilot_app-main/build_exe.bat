@echo off
cd /d "%~dp0"
pyinstaller --noconfirm --clean --name PaperPilot --windowed --onedir src\paperpilot_app.py
pause

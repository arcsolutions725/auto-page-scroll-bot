@echo off
echo Building Auto Scroll Bot executable...
echo.

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
pyinstaller --onefile --windowed --name "AutoScrollBot" --icon=NONE auto_scroll.py

echo.
echo Build complete! Check the 'dist' folder for AutoScrollBot.exe
pause




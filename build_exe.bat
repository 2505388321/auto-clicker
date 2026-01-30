@echo off
chcp 65001 >nul
echo ================================
echo   打包为 EXE
echo ================================
echo.
pip install pyautogui pynput pyinstaller -q
echo 打包中...
pyinstaller --onefile --windowed --name "自动点击器" auto_clicker.py
echo.
echo 完成: dist\自动点击器.exe
pause

@echo off
chcp 65001 >nul
title 自动点击器
color 0A

echo.
echo  ================================
echo     自动点击器 - 一键运行
echo  ================================
echo.

:: 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [错误] 未检测到 Python！
    echo.
    echo  请先安装 Python:
    echo.
    echo  1. 打开 https://www.python.org/downloads/
    echo  2. 下载并安装 Python
    echo  3. 安装时必须勾选 "Add Python to PATH"
    echo.
    echo  详细教程请看: 【必看】Python安装教程.txt
    echo.
    pause
    exit
)

echo  [√] Python 已安装
echo.
echo  [1/2] 安装依赖中...
pip install pyautogui pynput -q

if %errorlevel% neq 0 (
    color 0E
    echo.
    echo  [!] 依赖安装可能失败，尝试继续运行...
    echo.
)

echo  [2/2] 启动程序...
echo.
echo  --------------------------------
echo   快捷键: F1/F2获取位置
echo           F5开始  S停止
echo  --------------------------------
echo.

python auto_clicker.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [错误] 程序运行出错！
    echo.
    echo  可能的原因:
    echo  1. 依赖没装好，再运行一次试试
    echo  2. 把错误信息截图发给我
    echo.
)

pause

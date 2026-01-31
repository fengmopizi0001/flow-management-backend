@echo off
chcp 65001 > nul
title 流水管理系统 - 环境安装脚本

echo ========================================
echo   流水管理系统 - 环境安装脚本
echo ========================================
echo.

REM 检查Python环境
echo [1/5] 检查Python环境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python环境！
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python环境正常: %PYTHON_VERSION%
echo.

REM 检查pip
echo [2/5] 检查pip...
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip未正确安装
    pause
    exit /b 1
)
echo ✅ pip正常
echo.

REM 创建必要的目录
echo [3/5] 创建必要的目录结构...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
echo ✅ 目录结构创建完成
echo.

REM 升级pip
echo [4/5] 升级pip...
python -m pip install --upgrade pip
echo ✅ pip升级完成
echo.

REM 安装依赖包
echo [5/5] 安装项目依赖...
if exist "requirements.txt" (
    echo 从requirements.txt安装依赖...
    pip install -r requirements.txt
) else (
    echo requirements.txt不存在，安装核心依赖...
    pip install flask openpyxl
)

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败！
    pause
    exit /b 1
)

echo ✅ 依赖安装完成
echo.

REM 检查数据库
echo [6/6] 检查数据库...
if exist "data\flow.db" (
    echo ✅ 数据库文件已存在
) else (
    echo ℹ️  数据库文件不存在，首次启动时会自动创建
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步操作：
echo   1. 运行 start_background.bat 启动后台服务
echo   2. 或运行 启动新版本.bat 在前台启动
echo.
pause

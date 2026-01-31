@echo off
chcp 65001 >nul
title 流水管理系统 - 新版本

echo ========================================
echo 流水管理系统 - 启动中
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查是否需要安装依赖
if not exist "venv\" (
    echo [信息] 首次运行，正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [信息] 检查并安装依赖...
pip install -q flask openpyxl
if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能有问题，但继续尝试启动
)

REM 检查数据库
if not exist "data\" (
    echo [信息] 创建数据目录...
    mkdir data
)

echo.
echo ========================================
echo [成功] 系统启动成功！
echo ========================================
echo.
echo 访问地址: http://localhost:5000
echo 默认管理员账户: admin / admin123
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

REM 启动应用
python app_new.py

pause

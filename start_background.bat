@echo off
chcp 65001 > nul
title 流水管理系统 - 后台启动脚本

echo ========================================
echo   流水管理系统 - 后台服务启动
echo ========================================
echo.

REM 检查Python环境
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python环境未找到！请先运行 install.bat
    pause
    exit /b 1
)

REM 检查是否存在运行中的进程
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ⚠️  检测到Python进程正在运行
    echo.
    set /p CHOICE="是否停止现有进程并重新启动？(Y/N): "
    if /i "%CHOICE%"=="Y" (
        echo 正在停止现有进程...
        taskkill /F /IM python.exe > nul 2>&1
        timeout /t 2 > nul
    ) else (
        echo 启动已取消
        pause
        exit /b 0
    )
)

REM 设置环境变量为生产模式
set FLASK_CONFIG=production
set FLASK_ENV=production

echo 正在启动后台服务...
echo.
echo 服务信息：
echo   - 运行模式: 生产环境
echo   - 监听地址: 0.0.0.0:5000
echo   - 日志文件: logs\app.log
echo.

REM 使用pythonw启动（无窗口模式），重定向日志
start /MIN "流水管理系统" pythonw app_new.py > logs\app.log 2>&1

REM 等待服务启动
timeout /t 3 > nul

REM 检查服务是否成功启动
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo ========================================
    echo   ✅ 后台服务启动成功！
    echo ========================================
    echo.
    echo 服务正在后台运行，关闭此窗口不会影响服务
    echo.
    echo 访问地址：
    echo   - 本地: http://localhost:5000
    echo   - 局域网: http://YOUR_IP:5000
    echo.
    echo 管理命令：
    echo   - 查看状态: 运行 status.bat
    echo   - 停止服务: 运行 stop.bat
    echo   - 查看日志: 打开 logs\app.log
    echo.
) else (
    echo.
    echo ❌ 服务启动失败！
    echo 请查看 logs\app.log 了解详细错误信息
    echo.
)

pause

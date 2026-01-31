@echo off
chcp 65001 > nul
title 流水管理系统 - 服务状态检查

echo ========================================
echo   流水管理系统 - 服务状态
echo ========================================
echo.

REM 检查Python进程
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ 服务状态: 运行中
    echo.
    
    echo 进程信息：
    tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE
    
    echo.
    echo 端口监听状态：
    netstat -ano | findstr :5000
    
    echo.
    echo 访问地址：
    echo   - 本地: http://localhost:5000
    for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /C:"IPv4"') do (
        for /f "tokens=1" %%B in ("%%A") do (
            echo   - 局域网: http://%%B:5000
        )
    )
    
    echo.
    echo 日志文件：
    if exist "logs\app.log" (
        echo   - 最新日志: logs\app.log
        echo   - 文件大小:
        for %%A in ("logs\app.log") do (
            set SIZE=%%~zA
            set /a SIZE_MB=!SIZE!/1024/1024
            echo     !SIZE! 字节
        )
        echo.
        echo 最近10行日志：
        echo ========================================
        powershell -Command "Get-Content logs\app.log -Tail 10"
        echo ========================================
    ) else (
        echo   - 未找到日志文件
    )
    
) else (
    echo ❌ 服务状态: 未运行
    echo.
    echo 请运行 start_background.bat 启动服务
)

echo.
pause

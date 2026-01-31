@echo off
chcp 65001 > nul
title 流水管理系统 - 停止服务脚本

echo ========================================
echo   流水管理系统 - 停止后台服务
echo ========================================
echo.

REM 检查Python进程
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo 检测到后台Python进程正在运行
    echo.
    echo 正在停止服务...
    
    REM 尝试优雅关闭
    taskkill /F /IM pythonw.exe > nul 2>&1
    
    REM 等待进程结束
    timeout /t 2 > nul
    
    REM 检查是否成功停止
    tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo.
        echo ❌ 停止失败，尝试强制结束...
        taskkill /F /IM pythonw.exe /T > nul 2>&1
        timeout /t 1 > nul
    )
    
    REM 最终检查
    tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo.
        echo ❌ 无法停止服务，请手动结束进程
    ) else (
        echo.
        echo ========================================
        echo   ✅ 后台服务已停止
        echo ========================================
    )
) else (
    echo 未检测到运行中的后台服务
    echo.
    echo ℹ️  提示：如果您使用前台模式运行，请直接按 Ctrl+C 停止
)

echo.
pause

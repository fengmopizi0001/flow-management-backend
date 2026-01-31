@echo off
cd /d "%~dp0"
echo ==========================================
echo           Stopping Service...
echo ==========================================
echo.

echo Stopping background service (pythonw.exe)...
wmic process where "name='pythonw.exe' and commandline like '%%app_new.py%%'" call terminate >nul 2>&1

echo Stopping foreground service (python.exe)...
wmic process where "name='python.exe' and commandline like '%%app_new.py%%'" call terminate >nul 2>&1

echo.
echo [Done] Service stopped.
echo.

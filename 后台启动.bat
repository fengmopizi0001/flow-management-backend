@echo off
cd /d "%~dp0"
echo ==========================================
echo       Starting Service (Background)
echo ==========================================
echo.
echo Checking environment...

tasklist /FI "IMAGENAME eq pythonw.exe" | findstr /i "pythonw.exe" >nul
if %ERRORLEVEL% equ 0 (
    wmic process where "name='pythonw.exe' and commandline like '%%app_new.py%%'" get processid | findstr [0-9] >nul
    if %ERRORLEVEL% equ 0 (
        echo [Warning] System seems to be already running.
        echo.
        exit
    )
)

echo Starting service...
start "" pythonw app_new.py

echo.
echo [Success] Service started in background!
echo.
echo Access URL: http://localhost:5000
echo.

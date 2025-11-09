@echo off
REM ARVOS Web Viewer - Quick Start Script for Windows

echo.
echo 🚀 Starting ARVOS Web Viewer...
echo.

REM Detect port (default 8000)
if "%1"=="" (
    set PORT=8000
) else (
    set PORT=%1
)

echo 📡 Network Configuration:
echo    Port: %PORT%
echo.
echo 📱 iPhone Setup:
echo    1. Open ARVOS app
echo    2. Go to Stream tab
echo    3. Tap 'Connect to Server'
echo    4. Scan QR code from browser
echo.
echo 🌐 Opening browser at: http://localhost:%PORT%
echo.

REM Open browser
timeout /t 2 /nobreak >nul
start http://localhost:%PORT%

REM Start Python server
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Starting Python HTTP server...
    python -m http.server %PORT%
) else (
    echo ❌ Error: Python not found
    echo.
    echo Please install Python 3:
    echo    Download from: https://python.org/downloads
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

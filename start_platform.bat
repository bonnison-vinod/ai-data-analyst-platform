@echo off
echo ===============================================
echo AI Data Analyst Platform - Enterprise Edition
echo ===============================================
echo.
echo Checking requirements...

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check if Node.js is available
npm.cmd --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo ✓ Python and Node.js are available
echo.

echo Starting Backend Server...
cd Backend
if not exist "app\main.py" (
    echo ERROR: Backend files not found in Backend folder
    pause
    exit /b 1
)
start "AI Data Analyst - Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✓ Backend server starting on port 8000
timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Application...
cd ../frontend
if not exist "package.json" (
    echo ERROR: Frontend files not found in frontend folder
    pause
    exit /b 1
)
start "AI Data Analyst - Frontend" cmd /k "npm.cmd start"
echo ✓ Frontend application starting on port 3000

echo.
echo ===============================================
echo 🚀 Platform is starting up...
echo.
echo 📊 Frontend:  http://localhost:3000
echo 🔧 Backend:   http://localhost:8000  
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo ⚡ Features:
echo   • Modern split-screen login (Corporate/Personal)
echo   • Professional dashboard with analytics
echo   • File upload and AI-powered analysis
echo   • Real-time data visualization
echo.
echo 🔍 Troubleshooting:
echo   • If you see blank page, try hard refresh (Ctrl+Shift+R)
echo   • Check browser console (F12) for errors
echo   • Use debug_frontend.bat for detailed debugging
echo ===============================================
echo.
echo Press any key to close this window...
pause >nul

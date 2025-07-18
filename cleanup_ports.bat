@echo off
echo ================================================
echo Port Cleanup Script
echo ================================================
echo.
echo Checking what's running on ports 3000 and 8000...

echo.
echo === Port 3000 (Frontend) ===
netstat -ano | findstr :3000
echo.
echo === Port 8000 (Backend) ===
netstat -ano | findstr :8000

echo.
echo Killing all Node.js processes...
taskkill /f /im node.exe 2>nul
taskkill /f /im nodejs.exe 2>nul

echo.
echo Killing all Python processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo.
echo Killing any remaining processes on specific ports...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /f /pid %%a 2>nul

echo.
echo ✓ All processes cleaned up
echo.
echo Waiting 3 seconds for ports to be released...
timeout /t 3 /nobreak >nul

echo.
echo Checking ports again...
echo === Port 3000 ===
netstat -ano | findstr :3000
echo === Port 8000 ===
netstat -ano | findstr :8000

echo.
echo Ports should now be free!
echo You can now run start_platform.bat
echo.
pause

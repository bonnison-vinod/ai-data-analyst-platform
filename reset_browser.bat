@echo off
echo ================================================
echo Browser Reset Script
echo ================================================
echo.
echo Closing all browser processes...

:: Close all browser processes
taskkill /f /im chrome.exe 2>nul
taskkill /f /im msedge.exe 2>nul
taskkill /f /im firefox.exe 2>nul
taskkill /f /im iexplore.exe 2>nul

echo ✓ All browsers closed
echo.
echo Instructions for manual cache clearing:
echo.
echo For Chrome:
echo 1. Open Chrome
echo 2. Press Ctrl+Shift+Delete
echo 3. Select "All time" 
echo 4. Check all boxes
echo 5. Click "Clear data"
echo.
echo For Edge:
echo 1. Open Edge  
echo 2. Press Ctrl+Shift+Delete
echo 3. Select "All time"
echo 4. Check all boxes
echo 5. Click "Clear now"
echo.
echo Alternative: Try Incognito/Private mode first!
echo.
echo Starting development server in 5 seconds...
timeout /t 5 /nobreak >nul

cd frontend
npm.cmd start

pause

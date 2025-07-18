@echo off
echo ================================================
echo Frontend Debug Script
echo ================================================
echo.
echo Clearing all caches and temporary files...

echo 1. Removing node_modules cache...
cd frontend
rmdir /s /q node_modules\.cache 2>nul

echo 2. Removing build directory...
rmdir /s /q build 2>nul

echo 3. Clearing npm cache...
npm.cmd cache clean --force

echo 4. Reinstalling dependencies...
npm.cmd install

echo 5. Starting development server with verbose output...
echo.
echo ================================================
echo Open your browser to: http://localhost:3000
echo If you see "Practice" text, check browser:
echo - Open DevTools (F12)
echo - Check Console tab for errors
echo - Check Network tab for failed requests
echo - Try hard refresh (Ctrl+Shift+R)
echo ================================================
echo.

npm.cmd start

pause

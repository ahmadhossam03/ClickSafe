@echo off
echo Starting ClickSafe Flask API...
echo.

cd /d "c:\xampp\htdocs\grad\grad\url\urlScan"

echo Current directory: %CD%
echo.

echo Starting Flask API server on http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python api.py

pause

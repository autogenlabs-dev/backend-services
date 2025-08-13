@echo off
echo 🚀 Starting AutoGen Backend Server...
echo.
cd /d "D:\Autogen\Autogen-web-app\backend-services\user-management-backend"

echo 📂 Current directory: %CD%
echo.

echo 🐍 Starting Python server...
echo ⚠️ If you see any errors, please check the output below:
echo.
python minimal_auth_server.py

echo.
echo ❌ Server stopped. Press any key to exit...
pause >nul

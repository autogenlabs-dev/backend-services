@echo off
echo 🔧 Quick Redis Setup for Windows
echo.

REM Check if Redis is already running
echo 📡 Checking if Redis is running...
netstat -an | findstr ":6379" > nul
if %errorlevel% equ 0 (
    echo ✅ Redis is already running on port 6379!
    echo 🚀 You can restart your backend server now.
    pause
    exit /b 0
)

echo ❌ Redis is not running
echo.

echo 🛠️ Setting up Redis...
echo.

REM Create Redis directory
if not exist "C:\Redis" (
    echo 📁 Creating Redis directory...
    mkdir "C:\Redis"
)

REM Check if Redis executable exists
if exist "C:\Redis\redis-server.exe" (
    echo ✅ Redis found! Starting server...
    goto start_redis
)

echo 📥 Downloading Redis for Windows...
echo Please wait while we download Redis...

REM Download Redis (using PowerShell for download)
powershell -Command "& {try { Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip' -OutFile 'C:\Redis\redis.zip'; Write-Host '✅ Redis downloaded successfully!' } catch { Write-Host '❌ Download failed. Please download manually from: https://github.com/microsoftarchive/redis/releases'; exit 1 } }"

if %errorlevel% neq 0 (
    echo ❌ Download failed!
    echo 📋 Please download Redis manually:
    echo 1. Go to: https://github.com/microsoftarchive/redis/releases
    echo 2. Download Redis-x64-3.0.504.zip
    echo 3. Extract to C:\Redis\
    echo 4. Run this script again
    pause
    exit /b 1
)

echo 📦 Extracting Redis...
powershell -Command "Expand-Archive -Path 'C:\Redis\redis.zip' -DestinationPath 'C:\Redis\' -Force"

:start_redis
echo 🚀 Starting Redis server...
echo.
echo ✅ Redis will start in a new window
echo 🔌 Redis will be available on localhost:6379
echo.
echo ⚠️ Keep the Redis window open while using your application!
echo.

REM Start Redis server in a new window
start "Redis Server" "C:\Redis\redis-server.exe"

echo.
echo ✅ Redis setup complete!
echo 🚀 Now restart your backend server to use caching
echo.
pause

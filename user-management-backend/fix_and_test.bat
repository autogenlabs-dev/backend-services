@echo off
echo ========================================================
echo  FIX AND TEST SCRIPT FOR RAZORPAY INTEGRATION
echo ========================================================

echo.
echo [1/5] Installing local dependencies (requests, razorpay)...
pip install requests razorpay
if %errorlevel% neq 0 (
    echo Warning: Failed to install dependencies. You might need to run as admin or check python setup.
)

echo.
echo [2/5] Rebuilding Backend Container (forcing updates)...
docker-compose build --no-cache api
if %errorlevel% neq 0 (
    echo Error: Docker build failed.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/5] Starting Backend Container...
docker-compose up -d api
if %errorlevel% neq 0 (
    echo Error: Failed to start container.
    pause
    exit /b %errorlevel%
)

echo.
echo [4/5] Waiting for Backend to be ready (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo [5/5] Running End-to-End Payment Test...
python test_e2e_payment.py

echo.
echo ========================================================
echo  TEST COMPLETE
echo ========================================================
pause

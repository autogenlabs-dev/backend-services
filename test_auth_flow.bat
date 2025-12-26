@echo off
REM End-to-End Clerk Authentication Test Script for Windows

echo ============================================================
echo Clerk Authentication E2E Test Suite
echo ============================================================
echo.

cd user-management-backend

echo [1] Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend is not running!
    echo Please start the backend first:
    echo   cd user-management-backend
    echo   python -m uvicorn app.main:app --reload --port 8000
    echo.
    pause
    exit /b 1
)
echo [PASS] Backend is running
echo.

echo [2] Running Python test suite...
python test_clerk_e2e_flow.py

echo.
echo ============================================================
echo Test Complete
echo ============================================================
pause

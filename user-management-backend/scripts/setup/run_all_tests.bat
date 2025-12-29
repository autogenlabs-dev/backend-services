@echo off
echo ==========================================
echo 🚀 Setting up Environment and Running Tests
echo ==========================================

echo.
echo 🛑 Stopping existing containers...
docker-compose down

echo.
echo 🐳 Starting MongoDB and Redis...
docker-compose up -d mongodb redis

echo.
echo ⏳ Waiting 10 seconds for databases to initialize...
timeout /t 10 /nobreak

echo.
echo 🐍 Starting Backend Server (background)...
start /B python minimal_auth_server.py > server_log.txt 2>&1

echo.
echo ⏳ Waiting 10 seconds for server to start...
timeout /t 10 /nobreak

echo.
echo 🧪 Running End-to-End Payment Tests...
python test_e2e_payment.py

echo.
echo 🧪 Running Payment Flow Tests...
python test_payment_flow.py

echo.
echo ==========================================
echo ✅ Done! Check server_log.txt for server output.
echo ==========================================
pause

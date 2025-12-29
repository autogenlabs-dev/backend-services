@echo off
echo [1/5] Installing local dependencies...
pip install requests razorpay > pip_log.txt 2>&1

echo [2/5] Rebuilding Backend Container...
docker-compose build --no-cache api > docker_build_log.txt 2>&1

echo [3/5] Starting Backend Container...
docker-compose up -d api > docker_up_log.txt 2>&1

echo [4/5] Waiting for Backend...
timeout /t 15 /nobreak >nul

echo [5/5] Running End-to-End Payment Test...
python test_e2e_payment.py > e2e_auto_result.txt 2>&1

echo DONE.

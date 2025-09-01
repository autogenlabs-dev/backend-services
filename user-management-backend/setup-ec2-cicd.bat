@echo off
REM Windows PowerShell script to test EC2 connection and setup

echo ===================================================
echo EC2 CI/CD Setup for Windows
echo ===================================================
echo.

echo Your EC2 Instance Details:
echo   Public IP: 13.234.18.159
echo   DNS Name: ec2-13-234-18-159.ap-south-1.compute.amazonaws.com
echo   SSH User: ubuntu
echo   Key File: autogenlabs.pem
echo.

echo Steps to setup CI/CD:
echo.

echo 1. Test SSH Connection:
echo    ssh -i autogenlabs.pem ubuntu@13.234.18.159
echo.

echo 2. Get private key content for GitHub:
echo    type autogenlabs.pem
echo.

echo 3. Add GitHub Secrets:
echo    Go to: https://github.com/autogenlabs-dev/backend-services/settings/secrets/actions
echo.
echo    Add these secrets:
echo    - EC2_HOST: 13.234.18.159
echo    - EC2_USER: ubuntu
echo    - EC2_SSH_PRIVATE_KEY: [content of autogenlabs.pem]
echo.

echo 4. Setup EC2 (run on EC2 instance):
echo    sudo apt update ^&^& sudo apt upgrade -y
echo    sudo apt install -y python3-pip python3-venv nginx redis-server git curl
echo    git clone https://github.com/autogenlabs-dev/backend-services.git
echo    cd backend-services/user-management-backend
echo    chmod +x ec2-deploy.sh
echo    ./ec2-deploy.sh
echo.

echo 5. Test deployment:
echo    Push code to main branch and check GitHub Actions
echo.

echo ===================================================
echo Press any key to continue...
pause >nul

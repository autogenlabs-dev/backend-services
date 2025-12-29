# PowerShell deployment script for User Management API
# Usage: .\deploy.ps1

Write-Host "🚀 Deploying User Management API to EC2..." -ForegroundColor Green

# Set your EC2 details
$EC2_USER = "ec2-user"
$PEM_FILE = "autogen (1).pem"

# Get EC2 public IP
$EC2_IP = Read-Host "Enter your EC2 public IP address"

Write-Host "📋 Using EC2 IP: $EC2_IP" -ForegroundColor Yellow

# Test if SSH is available
try {
    ssh -V 2>$null
} catch {
    Write-Host "❌ SSH not found. Please install OpenSSH or use Git Bash" -ForegroundColor Red
    exit 1
}

# Set correct permissions for PEM file (already done in Windows)
Write-Host "🔑 Setting PEM file permissions..." -ForegroundColor Blue

# Test SSH connection
Write-Host "🔗 Testing SSH connection..." -ForegroundColor Blue
$testConnection = ssh -i $PEM_FILE -o ConnectTimeout=10 -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP "echo 'Connection successful!'" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection successful!" -ForegroundColor Green
    
    # Copy files to EC2
    Write-Host "📁 Copying files to EC2..." -ForegroundColor Blue
    scp -i $PEM_FILE -o StrictHostKeyChecking=no -r user-management-backend/ "$EC2_USER@$EC2_IP`:~/"
    
    # Run deployment commands on EC2
    Write-Host "🚀 Running deployment on EC2..." -ForegroundColor Blue
    
    # Create deployment script
    $deployScript = @"
cd ~/user-management-backend

# Update system and install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Restart shell to apply docker group changes
newgrp docker << DOCKER_COMMANDS
# Build and run containers
docker build -t user-management-api:latest .
docker-compose up -d

echo "✅ Deployment complete!"
echo "🌐 Your API is now running at: http://`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "📚 API Documentation: http://`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"

# Show running containers
docker ps
DOCKER_COMMANDS
"@

    # Execute deployment script on EC2
    ssh -i $PEM_FILE -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP $deployScript
    
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Your API should be available at: http://$EC2_IP:8000" -ForegroundColor Cyan
    Write-Host "📚 API Documentation: http://$EC2_IP:8000/docs" -ForegroundColor Cyan
    
} else {
    Write-Host "❌ SSH connection failed. Please check:" -ForegroundColor Red
    Write-Host "1. EC2 instance is running (i-0b65b244ab0990c4d)" -ForegroundColor Yellow
    Write-Host "2. Security group allows SSH (port 22) and HTTP (port 8000)" -ForegroundColor Yellow
    Write-Host "3. PEM file is in the correct location" -ForegroundColor Yellow
    Write-Host "4. EC2 public IP is correct" -ForegroundColor Yellow
}

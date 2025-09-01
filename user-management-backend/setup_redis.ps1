# Redis Setup Script for Windows
# This script helps set up Redis for the cache service

Write-Host "🔧 Redis Setup for Cache Service" -ForegroundColor Green

# Check if Redis is already running
Write-Host "📡 Checking if Redis is running..." -ForegroundColor Yellow
try {
    $result = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
    if ($result.TcpTestSucceeded) {
        Write-Host "✅ Redis is already running on port 6379!" -ForegroundColor Green
        Write-Host "🚀 You can restart your backend server now." -ForegroundColor Cyan
        exit 0
    }
} catch {
    Write-Host "❌ Redis is not running" -ForegroundColor Red
}

Write-Host "🛠️ Setting up Redis..." -ForegroundColor Yellow

# Option 1: Check if Chocolatey is available
Write-Host "📦 Checking for Chocolatey..." -ForegroundColor Yellow
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "✅ Chocolatey found! Installing Redis..." -ForegroundColor Green
    choco install redis-64 -y
    
    # Start Redis service
    Write-Host "🚀 Starting Redis service..." -ForegroundColor Yellow
    redis-server --service-install
    redis-server --service-start
    
    Write-Host "✅ Redis installed and started via Chocolatey!" -ForegroundColor Green
    exit 0
}

# Option 2: Check if Docker is available
Write-Host "🐳 Checking for Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker found! Starting Redis container..." -ForegroundColor Green
    
    # Stop any existing Redis container
    docker stop redis-cache 2>$null
    docker rm redis-cache 2>$null
    
    # Start new Redis container
    docker run -d --name redis-cache -p 6379:6379 redis:7-alpine
    
    Write-Host "✅ Redis started in Docker container!" -ForegroundColor Green
    Write-Host "🔌 Redis is now running on localhost:6379" -ForegroundColor Cyan
    exit 0
}

# Option 3: Manual installation instructions
Write-Host "⚠️ Neither Chocolatey nor Docker found." -ForegroundColor Yellow
Write-Host "📋 Please install Redis manually using one of these options:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option A - Install Chocolatey first, then Redis:" -ForegroundColor White
Write-Host "1. Open PowerShell as Administrator" -ForegroundColor Gray
Write-Host "2. Install Chocolatey (run the command from chocolatey.org)" -ForegroundColor Gray
Write-Host "3. Run: choco install redis-64 -y" -ForegroundColor Gray
Write-Host "4. Start Redis service" -ForegroundColor Gray
Write-Host ""
Write-Host "Option B - Install Docker Desktop:" -ForegroundColor White
Write-Host "1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
Write-Host "2. Install and restart your computer" -ForegroundColor Gray
Write-Host "3. Run: docker run -d -p 6379:6379 redis:7-alpine" -ForegroundColor Gray
Write-Host ""
Write-Host "Option C - Download Redis directly:" -ForegroundColor White
Write-Host "1. Download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Gray
Write-Host "2. Extract and run redis-server.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "🔥 Quick Test Commands:" -ForegroundColor Yellow
Write-Host "After setup, test with: redis-cli ping" -ForegroundColor Gray
Write-Host "Expected response: PONG" -ForegroundColor Gray

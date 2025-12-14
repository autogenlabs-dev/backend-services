# Clerk Authentication - Docker Restart Script (PowerShell)
# This script restarts the Docker containers with updated Clerk configuration

Write-Host "`n🔄 Clerk Authentication Setup - Restarting Docker Containers" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check if docker-compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker-compose is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Compose first"
    exit 1
}

Write-Host "Step 1: Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "`nStep 2: Removing old containers (optional)..." -ForegroundColor Yellow
$remove = Read-Host "Do you want to remove old containers? (y/N)"
if ($remove -eq "y" -or $remove -eq "Y") {
    docker-compose rm -f
    Write-Host "✅ Old containers removed" -ForegroundColor Green
}

Write-Host "`nStep 3: Rebuilding containers with new configuration..." -ForegroundColor Yellow
docker-compose build --no-cache api

Write-Host "`nStep 4: Starting containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`nStep 5: Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if containers are running
$containersStatus = docker-compose ps
if ($containersStatus -match "Up") {
    Write-Host "✅ Containers are running" -ForegroundColor Green
} else {
    Write-Host "❌ Containers failed to start" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs"
    exit 1
}

Write-Host "`nStep 6: Verifying environment variables..." -ForegroundColor Yellow
docker-compose exec -T api env | Select-String "CLERK"

Write-Host "`nStep 7: Testing health endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    if ($response.status -eq "ok") {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot connect to backend" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green

Write-Host "Next steps:"
Write-Host "1. View logs: docker-compose logs -f api"
Write-Host "2. Run diagnostic test: python test_clerk_auth_flow.py"
Write-Host "3. Test with frontend at http://localhost:3000"
Write-Host ""
Write-Host "Troubleshooting:"
Write-Host "- Check logs: docker-compose logs api"
Write-Host "- Restart: docker-compose restart api"
Write-Host "- Shell access: docker-compose exec api bash"
Write-Host ""

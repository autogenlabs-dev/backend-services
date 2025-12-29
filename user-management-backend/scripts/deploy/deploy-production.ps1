# Production Deployment Script for User Management Backend (PowerShell)
Write-Host "🚀 Starting production deployment..." -ForegroundColor Green

# Set production environment
$env:ENVIRONMENT = "production"

# Load production environment variables
if (Test-Path ".env.production") {
    Write-Host "📄 Loading production environment variables..." -ForegroundColor Yellow
    Get-Content .env.production | ForEach-Object {
        if ($_ -match "^([^#].*)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "❌ .env.production file not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run database migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

# Get port from environment or default to 8000
$port = if ($env:PORT) { $env:PORT } else { "8000" }
$serverHost = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }

# Start the application
Write-Host "🌟 Starting production server on port $port..." -ForegroundColor Green
uvicorn app.main:app --host $serverHost --port $port --workers 4

Write-Host "✅ Production deployment completed!" -ForegroundColor Green

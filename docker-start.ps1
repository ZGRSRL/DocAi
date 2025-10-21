# SAPDOCAI Docker Start Script
# PowerShell script to start SAPDOCAI with Docker

Write-Host "🚀 Starting SAPDOCAI with Docker..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
Write-Host "📊 Container Status:" -ForegroundColor Cyan
docker-compose ps

# Show access information
Write-Host "`n🎯 SAPDOCAI is now running!" -ForegroundColor Green
Write-Host "📱 Web Application: http://localhost:8501" -ForegroundColor White
Write-Host "🗄️ MySQL: localhost:3306" -ForegroundColor White
Write-Host "🐘 PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "🔴 Redis: localhost:6379" -ForegroundColor White
Write-Host "🍃 MongoDB: localhost:27017" -ForegroundColor White

Write-Host "`n📚 For more information, see DOCKER_README.md" -ForegroundColor Cyan
Write-Host "🛑 To stop: docker-compose down" -ForegroundColor Yellow

# Open browser
Start-Sleep -Seconds 2
Write-Host "`n🌐 Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

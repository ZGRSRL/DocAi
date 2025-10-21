# SAPDOCAI Docker Development Script
# PowerShell script to start SAPDOCAI in development mode

Write-Host "🔧 Starting SAPDOCAI in Development Mode..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start development services
Write-Host "🐳 Starting development containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
Write-Host "📊 Development Container Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.dev.yml ps

# Show access information
Write-Host "`n🎯 SAPDOCAI Development Mode is running!" -ForegroundColor Green
Write-Host "📱 Web Application: http://localhost:8501" -ForegroundColor White
Write-Host "🗄️ MySQL: localhost:3306" -ForegroundColor White
Write-Host "🔄 Hot Reload: Enabled" -ForegroundColor White

Write-Host "`n📚 Development Features:" -ForegroundColor Cyan
Write-Host "  • Hot reload enabled" -ForegroundColor White
Write-Host "  • Volume mounting for live code changes" -ForegroundColor White
Write-Host "  • Debug logging enabled" -ForegroundColor White

Write-Host "`n📖 To view logs: docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor Yellow
Write-Host "🛑 To stop: docker-compose -f docker-compose.dev.yml down" -ForegroundColor Yellow

# Open browser
Start-Sleep -Seconds 2
Write-Host "`n🌐 Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

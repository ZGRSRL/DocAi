# SAPDOCAI Docker Stop Script
# PowerShell script to stop SAPDOCAI Docker containers

Write-Host "🛑 Stopping SAPDOCAI Docker containers..." -ForegroundColor Yellow

# Stop and remove containers
docker-compose down

Write-Host "✅ SAPDOCAI containers stopped" -ForegroundColor Green

# Show remaining containers
Write-Host "`n📊 Remaining containers:" -ForegroundColor Cyan
docker ps -a

Write-Host "`n💡 To remove all data volumes, run: docker-compose down -v" -ForegroundColor Yellow
Write-Host "🔄 To restart, run: .\docker-start.ps1" -ForegroundColor Cyan

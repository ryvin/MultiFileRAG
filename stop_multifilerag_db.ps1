# PowerShell script to stop MultiFileRAG database containers
Write-Host "Stopping MultiFileRAG database containers..." -ForegroundColor Yellow

# Stop the database containers
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stop database containers." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Database containers stopped successfully." -ForegroundColor Green

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host

# Redeploy Docker compose and remove containers exposing port 8000 if found
# Run with PowerShell (from project root):
#   powershell -ExecutionPolicy Bypass -File .\docker_redeploy.ps1

Write-Host "Stopping and removing compose services..." -ForegroundColor Cyan
docker-compose down

Write-Host "Searching for containers exposing port 8000..." -ForegroundColor Cyan
$matches = docker ps -a --format "{{.ID}} {{.Names}} {{.Ports}}" | Select-String ":8000"
if ($matches) {
    Write-Host "Found containers exposing :8000 - removing..." -ForegroundColor Yellow
    $ids = $matches -replace '^([0-9a-f]+).*', '$1'
    foreach ($id in $ids) {
        Write-Host "Removing container $id" -ForegroundColor Yellow
        docker rm -f $id
    }
} else {
    Write-Host "No containers found exposing :8000" -ForegroundColor Green
}

Write-Host "Building images (no cache)..." -ForegroundColor Cyan
docker-compose build --no-cache

Write-Host "Starting services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "Showing compose status..." -ForegroundColor Cyan
docker-compose ps

Write-Host "Tailing backend logs (last 200 lines)..." -ForegroundColor Cyan
docker logs backend --tail 200

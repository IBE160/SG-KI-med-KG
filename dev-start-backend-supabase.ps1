# dev-start-backend-supabase.ps1
# Start backend with Supabase configuration from .env file
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Starting Backend with Supabase..." -ForegroundColor Green
Set-Location backend

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found in backend directory!" -ForegroundColor Red
    Write-Host "Please ensure backend/.env is configured with your Supabase credentials" -ForegroundColor Yellow
    exit 1
}

# Ensure deps are installed and up to date
Write-Host "Syncing dependencies..." -ForegroundColor Cyan
uv sync

# Start server (will load .env automatically)
Write-Host "Starting Server with Supabase..." -ForegroundColor Cyan
Write-Host "Backend API will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API docs available at: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

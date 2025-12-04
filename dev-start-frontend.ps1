# dev-start-frontend.ps1
$env:API_BASE_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"

Write-Host "Starting Frontend..."
Set-Location frontend
npm run dev

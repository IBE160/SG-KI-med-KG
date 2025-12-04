# dev-test-backend.ps1
$env:DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
$env:TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
$env:SECRET_KEY = "dev-secret-key"
$env:ACCESS_SECRET_KEY = "dev-access-secret"
$env:RESET_PASSWORD_SECRET_KEY = "dev-reset-secret"
$env:VERIFICATION_SECRET_KEY = "dev-verification-secret"
$env:CORS_ORIGINS = '["http://localhost:3000"]'

Write-Host "Running Backend Tests with SQLite (Async)..."
Set-Location backend
uv run pytest
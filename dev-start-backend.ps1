# dev-start-backend.ps1
$env:DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
$env:SECRET_KEY = "dev-secret-key"
$env:ACCESS_SECRET_KEY = "dev-access-secret"
$env:RESET_PASSWORD_SECRET_KEY = "dev-reset-secret"
$env:VERIFICATION_SECRET_KEY = "dev-verification-secret"
# Allow both 3000 (default) and 3001 (fallback)
$env:CORS_ORIGINS = '["http://localhost:3000", "http://localhost:3001"]'

Write-Host "Starting Backend with SQLite (dev.db)..."
Set-Location backend

# Ensure deps are installed and up to date
Write-Host "Syncing dependencies..."
uv sync

# Run migrations to create tables in SQLite
Write-Host "Running Migrations..."
uv run alembic upgrade head

# Start server
Write-Host "Starting Server..."
uv run fastapi dev app/main.py
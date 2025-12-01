# Script to populate database with initial data
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Populating Database with Initial Data" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
$serverCppPath = Join-Path $projectRoot "server_cpp"
$webFlaskPath = Join-Path $projectRoot "web_flask"

# Find database path
$dbPath1 = Join-Path $serverCppPath "data\voting.db"
$dbPath2 = Join-Path $serverCppPath "build\data\voting.db"

$dbPath = $null
if (Test-Path $dbPath1) {
    $dbPath = $dbPath1
    Write-Host "Found database at: $dbPath" -ForegroundColor Green
} elseif (Test-Path $dbPath2) {
    $dbPath = $dbPath2
    Write-Host "Found database at: $dbPath" -ForegroundColor Green
} else {
    # Create data directory and database will be created by server
    $dataDir = Join-Path $serverCppPath "data"
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
        Write-Host "Created data directory: $dataDir" -ForegroundColor Yellow
    }
    $dbPath = $dbPath1
    Write-Host "Database will be created at: $dbPath" -ForegroundColor Yellow
}

# Check if JSON file exists
$jsonFile = Join-Path $webFlaskPath "data\teams.json"
if (-not (Test-Path $jsonFile)) {
    Write-Host "ERROR: teams.json not found at: $jsonFile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Populating database from: $jsonFile" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/teams" -TimeoutSec 2 -ErrorAction Stop
    $backendRunning = $true
    Write-Host "Backend is running, using API to populate..." -ForegroundColor Green
} catch {
    Write-Host "Backend is not running, populating directly to database..." -ForegroundColor Yellow
}

if ($backendRunning) {
    # Use API method
    $populateScript = Join-Path $webFlaskPath "populate_database.py"
    if (Test-Path $populateScript) {
        python $populateScript
    } else {
        Write-Host "ERROR: populate_database.py not found!" -ForegroundColor Red
        exit 1
    }
} else {
    # Use direct database method
    $populateScript = Join-Path $webFlaskPath "populate_database_direct.py"
    if (Test-Path $populateScript) {
        python $populateScript $jsonFile $dbPath
    } else {
        Write-Host "ERROR: populate_database_direct.py not found!" -ForegroundColor Red
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Database populated successfully!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check database contents
    if (Test-Path $dbPath) {
        Write-Host "Checking database contents..." -ForegroundColor Cyan
        python (Join-Path $serverCppPath "check_database.py") $dbPath
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to populate database!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"



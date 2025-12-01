# PowerShell script for running the Football Voting System

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Football Voting System" -ForegroundColor Green
Write-Host "  C++ Backend + Flask Frontend" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
$pythonCmd = "python"

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}
catch {
    try {
        $pythonVersion = python3 --version 2>&1
        Write-Host "Found: $pythonVersion" -ForegroundColor Green
        $pythonCmd = "python3"
    }
    catch {
        Write-Host "ERROR: Python not found!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Kill old processes
Write-Host "Cleaning up old processes..." -ForegroundColor Yellow
Get-Process -Name "voting_server" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match "Flask" } | Stop-Process -Force

Write-Host ""

# Function to run process in new window
function Start-InNewWindow {
    param([string]$Title, [string]$Command, [string]$WorkingDirectory)
    
    Write-Host "Starting: $Title" -ForegroundColor Yellow
    
    if (-not (Test-Path $WorkingDirectory)) {
        Write-Host "ERROR: Directory not found: $WorkingDirectory" -ForegroundColor Red
        return $false
    }
    
    Start-Process powershell.exe -WorkingDirectory $WorkingDirectory -ArgumentList "-NoExit", "-Command", $Command
    Start-Sleep -Seconds 2
    return $true
}

# Function to build backend if needed
function Build-Backend {
    param([string]$ServerCppPath, [bool]$ForceRebuild = $false)
    
    $buildPath = Join-Path $ServerCppPath "build"
    if (-not (Test-Path $buildPath)) {
        New-Item -ItemType Directory -Path $buildPath -Force | Out-Null
    }
    
    Write-Host "Building Backend..." -ForegroundColor Yellow
    
    Push-Location $buildPath
    try {
        if ($ForceRebuild -or -not (Test-Path "CMakeCache.txt")) {
            Write-Host "Running CMake configuration..." -ForegroundColor Cyan
            cmake .. 
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: CMake configuration failed!" -ForegroundColor Red
                return $false
            }
        }
        
        Write-Host "Compiling..." -ForegroundColor Cyan
        $buildResult = cmake --build . --config Release 2>&1
        $buildExitCode = $LASTEXITCODE
        
        # Check if executable was actually created
        $exeFound = $false
        $exePaths = @("bin\Release\voting_server.exe", "Release\voting_server.exe")
        foreach ($exePath in $exePaths) {
            if (Test-Path $exePath) {
                $exeFound = $true
                break
            }
        }
        
        if (-not $exeFound) {
            Write-Host "ERROR: Build failed - executable not found!" -ForegroundColor Red
            if ($buildExitCode -ne 0) {
                Write-Host "Build exit code: $buildExitCode" -ForegroundColor Yellow
                Write-Host "Last 10 lines of build output:" -ForegroundColor Yellow
                $buildResult | Select-Object -Last 10 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
            }
            return $false
        }
        
        if ($buildExitCode -ne 0) {
            Write-Host "WARNING: Build reported errors but executable was created" -ForegroundColor Yellow
        }
        
        Write-Host "Backend built successfully!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "ERROR: Build error: $_" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
}

# Show menu
Write-Host "Select components to run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. C++ Backend Server only" -ForegroundColor Yellow
Write-Host "  2. Flask Web Frontend only" -ForegroundColor Yellow
Write-Host "  3. Both (Backend + Frontend)" -ForegroundColor Yellow
Write-Host "  4. Rebuild Backend (force clean build)" -ForegroundColor Yellow
Write-Host "  5. Exit" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Your choice (1-5)"

$serverCppPath = Join-Path $projectRoot "server_cpp"
$webFlaskPath = Join-Path $projectRoot "web_flask"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting C++ Backend Server..." -ForegroundColor Yellow
        
        if (-not (Build-Backend $serverCppPath)) {
            Write-Host "Failed to build backend!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        $buildPath = Join-Path $serverCppPath "build"
        $exePath1 = Join-Path $buildPath "bin\Release\voting_server.exe"
        $exePath2 = Join-Path $buildPath "Release\voting_server.exe"
        
        if (Test-Path $exePath1) {
            $backendCmd1 = ".\bin\Release\voting_server.exe"
            Start-InNewWindow "C++ Backend Server" $backendCmd1 $buildPath
        }
        elseif (Test-Path $exePath2) {
            $backendCmd2 = ".\Release\voting_server.exe"
            Start-InNewWindow "C++ Backend Server" $backendCmd2 $buildPath
        }
        else {
            Write-Host "ERROR: voting_server.exe not found after build!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Write-Host ""
        Write-Host "[OK] Backend Server started!" -ForegroundColor Green
        Write-Host "API available at: http://localhost:8080/api" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Write-Host "Starting Flask Web Frontend..." -ForegroundColor Yellow
        
        if (-not (Test-Path $webFlaskPath)) {
            Write-Host "ERROR: web_flask directory not found!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        # Check and install Flask dependencies
        Write-Host "Checking Flask dependencies..." -ForegroundColor Yellow
        & $pythonCmd -c "import flask; import flask_session; import requests" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing Flask dependencies..." -ForegroundColor Yellow
            $requirementsPath = Join-Path $webFlaskPath "requirements.txt"
            if (Test-Path $requirementsPath) {
                & $pythonCmd -m pip install -q -r $requirementsPath
            }
            else {
                Write-Host "WARNING: requirements.txt not found!" -ForegroundColor Yellow
            }
        }
        
        $env:FLASK_APP = "app.py"
        if (-not $env:API_BASE_URL) {
            $env:API_BASE_URL = "http://localhost:8080/api"
        }
        
        $flaskCmd = "$pythonCmd -m flask run --port 5000"
        Start-InNewWindow "Flask Web Frontend" $flaskCmd $webFlaskPath
        
        Write-Host ""
        Write-Host "[OK] Web Frontend started!" -ForegroundColor Green
        Write-Host "Open browser: http://localhost:5000" -ForegroundColor Cyan
    }
    
    "3" {
        Write-Host ""
        Write-Host "Starting all components..." -ForegroundColor Yellow
        Write-Host ""
        
        # Build and start C++ Backend
        Write-Host "[OK] Building and starting C++ Backend..." -ForegroundColor Green
        if (-not (Build-Backend $serverCppPath)) {
            Write-Host "Failed to build backend!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        $buildPath = Join-Path $serverCppPath "build"
        $exePath1 = Join-Path $buildPath "bin\Release\voting_server.exe"
        $exePath2 = Join-Path $buildPath "Release\voting_server.exe"
        
        if (Test-Path $exePath1) {
            $backendCmd1 = ".\bin\Release\voting_server.exe"
            Start-InNewWindow "C++ Backend Server" $backendCmd1 $buildPath
        }
        elseif (Test-Path $exePath2) {
            $backendCmd2 = ".\Release\voting_server.exe"
            Start-InNewWindow "C++ Backend Server" $backendCmd2 $buildPath
        }
        else {
            Write-Host "ERROR: voting_server.exe not found!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Start-Sleep -Seconds 3
        
        # Start Flask Frontend
        Write-Host "[OK] Starting Flask Web Frontend..." -ForegroundColor Green
        
        if (-not (Test-Path $webFlaskPath)) {
            Write-Host "ERROR: web_flask directory not found!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        # Check and install Flask dependencies
        Write-Host "Checking Flask dependencies..." -ForegroundColor Yellow
        & $pythonCmd -c "import flask; import flask_session; import requests" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing Flask dependencies..." -ForegroundColor Yellow
            $requirementsPath = Join-Path $webFlaskPath "requirements.txt"
            if (Test-Path $requirementsPath) {
                & $pythonCmd -m pip install -q -r $requirementsPath
            }
        }
        
        $env:FLASK_APP = "app.py"
        if (-not $env:API_BASE_URL) {
            $env:API_BASE_URL = "http://localhost:8080/api"
        }
        
        $flaskCmd = "$pythonCmd -m flask run --port 5000"
        Start-InNewWindow "Flask Web Frontend" $flaskCmd $webFlaskPath
        
        Write-Host ""
        Write-Host "All components started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Available endpoints:" -ForegroundColor Yellow
        Write-Host "  - C++ API Server:     http://localhost:8080/api" -ForegroundColor Cyan
        Write-Host "  - Web Frontend:        http://localhost:5000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Open your browser and go to:" -ForegroundColor Green
        Write-Host "  http://localhost:5000" -ForegroundColor White -BackgroundColor DarkBlue
    }
    
    "4" {
        Write-Host ""
        Write-Host "Rebuilding Backend (clean build)..." -ForegroundColor Yellow
        
        $buildPath = Join-Path $serverCppPath "build"
        if (Test-Path $buildPath) {
            Write-Host "Removing old build directory..." -ForegroundColor Cyan
            Remove-Item -Path $buildPath -Recurse -Force
        }
        
        if (-not (Build-Backend $serverCppPath $true)) {
            Write-Host "Failed to rebuild backend!" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Write-Host ""
        Write-Host "[OK] Backend rebuilt successfully!" -ForegroundColor Green
        Write-Host "You can now start the server using option 1 or 3" -ForegroundColor Cyan
        Read-Host "Press Enter to exit"
        exit 0
    }
    
    "5" {
        exit 0
    }
    
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Components started successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
pause

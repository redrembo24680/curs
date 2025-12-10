# Quick Start - Voting System

## Start Services
```powershell
docker-compose up -d --build
```

## Run Tests
```powershell
# Unit tests
docker exec curs-flask-1 python run_tests.py

# Voting functionality test
.\test_voting.ps1
```

## Vote via API
```powershell
# Vote for player 1 in match 11
$vote = @{match_id=11; player_id=1} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/vote" -Method Post -Body $vote -ContentType "application/json"
```

## Check Results
```powershell
# Get votes for match
Invoke-RestMethod -Uri "http://localhost:8080/api/votes?match_id=11"

# Get overall stats
Invoke-RestMethod -Uri "http://localhost:8080/api/stats"
```

## Access Web Interface
- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8080

## Restart Services
```powershell
docker-compose restart
```

## View Logs
```powershell
docker logs curs-flask-1       # Flask logs
docker logs curs-cpp_backend-1  # C++ backend logs
```

## Stop Services
```powershell
docker-compose down
```

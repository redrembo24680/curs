# Test voting functionality
Write-Host "=== Testing Voting System ===" -ForegroundColor Green
Write-Host ""

# 1. Get active matches
Write-Host "1. Getting active matches:" -ForegroundColor Cyan
$matchesResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/matches-page" -Method Get
Write-Host "Found $($matchesResponse.matches.Count) matches" -ForegroundColor Yellow
$firstMatch = $matchesResponse.matches[0]
Write-Host "First match: $($firstMatch.team1) vs $($firstMatch.team2) (ID: $($firstMatch.id))" -ForegroundColor Yellow
Write-Host ""

# 2. Get players list
Write-Host "2. Getting players list:" -ForegroundColor Cyan
$playersResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/players" -Method Get
Write-Host "Found $($playersResponse.players.Count) players" -ForegroundColor Yellow
$firstPlayer = $playersResponse.players[0]
Write-Host "First player: $($firstPlayer.name) (ID: $($firstPlayer.id), Position: $($firstPlayer.position))" -ForegroundColor Yellow
Write-Host ""

# 3. Vote for player in match
Write-Host "3. Voting for player $($firstPlayer.name) in match $($firstMatch.id):" -ForegroundColor Cyan
$voteBody = @{
    match_id = $firstMatch.id
    player_id = $firstPlayer.id
} | ConvertTo-Json

try {
    $voteResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/vote" -Method Post -Body $voteBody -ContentType "application/json"
    Write-Host "Status: $($voteResponse.status)" -ForegroundColor Green
    Write-Host "Message: $($voteResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "Error voting: $_" -ForegroundColor Red
}
Write-Host ""

# 4. Check votes for match
Write-Host "4. Checking votes for match $($firstMatch.id):" -ForegroundColor Cyan
try {
    $votesResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/votes?match_id=$($firstMatch.id)" -Method Get
    Write-Host "Votes for match $($firstMatch.id): $($votesResponse.votes.Count)" -ForegroundColor Yellow
    if ($votesResponse.votes.Count -gt 0) {
        Write-Host "Top 3 players with most votes:" -ForegroundColor Yellow
        $votesResponse.votes | Sort-Object -Property votes -Descending | Select-Object -First 3 | ForEach-Object {
            Write-Host "  - $($_.player_name): $($_.votes) vote(s)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "Error getting votes: $_" -ForegroundColor Red
}
Write-Host ""

# 5. Check statistics
Write-Host "5. Checking overall statistics:" -ForegroundColor Cyan
try {
    $statsResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/stats" -Method Get
    Write-Host "Total votes: $($statsResponse.total_votes)" -ForegroundColor Yellow
    Write-Host "Active matches: $($statsResponse.active_matches)" -ForegroundColor Yellow
    Write-Host "Total players: $($statsResponse.total_players)" -ForegroundColor Yellow
} catch {
    Write-Host "Error getting statistics: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Testing Complete ===" -ForegroundColor Green

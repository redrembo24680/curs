// Matches page functionality
let currentMatchId = null;
let userHasVoted = false;
let votedPlayerId = null;

// Football formation schemes
// Format: { positions: [{x, y, position}], name: "4-3-3" }
const formations = {
    "4-3-3": {
        name: "4-3-3",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 25, pos: "LB" }, { x: 10, y: 45, pos: "CB" }, { x: 10, y: 55, pos: "CB" }, { x: 10, y: 75, pos: "RB" },
            { x: 20, y: 40, pos: "CM" }, { x: 20, y: 50, pos: "CM" }, { x: 20, y: 60, pos: "CM" },
            { x: 40, y: 20, pos: "LW" }, { x: 40, y: 50, pos: "ST" }, { x: 40, y: 80, pos: "RW" }
        ]
    },
    "4-4-2": {
        name: "4-4-2",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 25, pos: "LB" }, { x: 10, y: 45, pos: "CB" }, { x: 10, y: 55, pos: "CB" }, { x: 10, y: 75, pos: "RB" },
            { x: 20, y: 28, pos: "LM" }, { x: 20, y: 45, pos: "CM" }, { x: 20, y: 55, pos: "CM" }, { x: 20, y: 72, pos: "RM" },
            { x: 40, y: 42, pos: "ST" }, { x: 40, y: 58, pos: "ST" }
        ]
    },
    "4-2-3-1": {
        name: "4-2-3-1",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 25, pos: "LB" }, { x: 10, y: 45, pos: "CB" }, { x: 10, y: 55, pos: "CB" }, { x: 10, y: 75, pos: "RB" },
            { x: 15, y: 45, pos: "CDM" }, { x: 15, y: 55, pos: "CDM" },
            { x: 35, y: 28, pos: "LW" }, { x: 35, y: 50, pos: "CAM" }, { x: 35, y: 72, pos: "RW" },
            { x: 45, y: 50, pos: "ST" }
        ]
    },
    "3-5-2": {
        name: "3-5-2",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 40, pos: "CB" }, { x: 10, y: 50, pos: "CB" }, { x: 10, y: 60, pos: "CB" },
            { x: 20, y: 20, pos: "LWB" }, { x: 20, y: 40, pos: "CM" }, { x: 20, y: 50, pos: "CM" }, { x: 20, y: 60, pos: "CM" }, { x: 20, y: 80, pos: "RWB" },
            { x: 40, y: 42, pos: "ST" }, { x: 40, y: 58, pos: "ST" }
        ]
    },
    "4-5-1": {
        name: "4-5-1",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 25, pos: "LB" }, { x: 10, y: 45, pos: "CB" }, { x: 10, y: 55, pos: "CB" }, { x: 10, y: 75, pos: "RB" },
            { x: 20, y: 20, pos: "LM" }, { x: 20, y: 40, pos: "CM" }, { x: 20, y: 50, pos: "CM" }, { x: 20, y: 60, pos: "CM" }, { x: 20, y: 80, pos: "RM" },
            { x: 40, y: 50, pos: "ST" }
        ]
    },
    "3-4-3": {
        name: "3-4-3",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 40, pos: "CB" }, { x: 10, y: 50, pos: "CB" }, { x: 10, y: 60, pos: "CB" },
            { x: 20, y: 28, pos: "LM" }, { x: 20, y: 45, pos: "CM" }, { x: 20, y: 55, pos: "CM" }, { x: 20, y: 72, pos: "RM" },
            { x: 40, y: 20, pos: "LW" }, { x: 40, y: 50, pos: "ST" }, { x: 40, y: 80, pos: "RW" }
        ]
    },
    "5-3-2": {
        name: "5-3-2",
        positions: [
            { x: 3, y: 50, pos: "GK" },
            { x: 10, y: 20, pos: "LWB" }, { x: 10, y: 40, pos: "CB" }, { x: 10, y: 50, pos: "CB" }, { x: 10, y: 60, pos: "CB" }, { x: 10, y: 80, pos: "RWB" },
            { x: 20, y: 40, pos: "CM" }, { x: 20, y: 50, pos: "CM" }, { x: 20, y: 60, pos: "CM" },
            { x: 40, y: 42, pos: "ST" }, { x: 40, y: 58, pos: "ST" }
        ]
    }
};

// Default formation if not specified
const defaultFormation = "4-3-3";

// Position mapping for players - realistic football field positions
// X: 0-100 (0 = left goal, 100 = right goal)
// Y: 0-100 (0 = top, 100 = bottom)
// Based on real football formations
const positionMap = {
    // Goalkeeper - very close to goal line
    "GK": { x: 3, y: 50 },

    // Defenders - defensive line (near penalty box)
    "CB": { x: 20, y: 50 },       // Center Back - central defense
    "LCB": { x: 20, y: 45 },      // Left Center Back
    "RCB": { x: 20, y: 55 },      // Right Center Back
    "LB": { x: 20, y: 25 },       // Left Back - left side defense
    "RB": { x: 20, y: 75 },       // Right Back - right side defense
    "LWB": { x: 22, y: 22 },      // Left Wing Back
    "RWB": { x: 22, y: 78 },      // Right Wing Back

    // Defensive Midfielders - defensive midfield (between defense and center)
    "CDM": { x: 30, y: 50 },      // Central Defensive Midfielder
    "LDM": { x: 30, y: 42 },      // Left Defensive Midfielder
    "RDM": { x: 30, y: 58 },      // Right Defensive Midfielder

    // Midfielders - center of field (around center circle)
    "CM": { x: 35, y: 50 },       // Central Midfielder - center circle
    "LCM": { x: 35, y: 45 },      // Left Central Midfielder
    "RCM": { x: 35, y: 55 },      // Right Central Midfielder
    "LM": { x: 35, y: 28 },       // Left Midfielder - wide left
    "RM": { x: 35, y: 72 },       // Right Midfielder - wide right
    "CAM": { x: 35, y: 65 },      // Central Attacking Midfielder
    "LAM": { x: 35, y: 42 },      // Left Attacking Midfielder
    "RAM": { x: 35, y: 58 },      // Right Attacking Midfielder

    // Wingers - wide attacking positions (near touchlines)
    "LW": { x: 30, y: 20 },       // Left Winger - wide left attack
    "RW": { x: 30, y: 80 },       // Right Winger - wide right attack
    "LF": { x: 35, y: 28 },       // Left Forward
    "RF": { x: 35, y: 72 },       // Right Forward

    // Forwards - attacking positions (near opponent's goal)
    "ST": { x: 40, y: 50 },       // Striker - center forward (near goal)
    "CF": { x: 52, y: 50 },       // Center Forward
    "LS": { x: 45, y: 45 },       // Left Striker
    "RS": { x: 45, y: 55 },       // Right Striker
};

// Load matches
async function loadMatches() {
    const data = await api.get('/matches-page', { matches: [], teams: [] });
    const matches = data.matches || [];
    const teams = data.teams || [];
    const select = document.getElementById('match-select');

    // Load teams for admin form
    const team1Select = document.getElementById('create-team1');
    const team2Select = document.getElementById('create-team2');
    if (team1Select && team2Select && teams.length > 0) {
        const teamOptions = teams.map(t => `<option value="${t.name}">${t.name}</option>`).join('');
        team1Select.innerHTML = '<option value="">Оберіть команду...</option>' + teamOptions;
        team2Select.innerHTML = '<option value="">Оберіть команду...</option>' + teamOptions;
    }

    // Check if user is admin (simple check - in production use proper auth)
    const adminForm = document.getElementById('admin-match-form');
    if (adminForm) {
        // Show admin form (you can add proper admin check here)
        adminForm.style.display = 'block';
    }

    if (matches.length === 0) {
        select.innerHTML = '<option value="">Немає матчів</option>';
        return;
    }

    select.innerHTML = '<option value="">Оберіть матч...</option>' +
        matches.map(m => `<option value="${m.id}">${m.team1} vs ${m.team2} - ${m.isActive ? 'Активний' : 'Завершено'}</option>`).join('');

    select.addEventListener('change', (e) => {
        if (e.target.value) {
            loadMatchData(parseInt(e.target.value));
        } else {
            document.getElementById('pitch-section').style.display = 'none';
        }
    });

    // Auto-select first match
    if (matches.length > 0 && matches[0].isActive) {
        select.value = matches[0].id;
        loadMatchData(matches[0].id);
    }
}

// Handle match creation
async function handleCreateMatch(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const matchData = {
        team1: formData.get('team1'),
        team2: formData.get('team2'),
        team1_formation: formData.get('team1_formation') || '4-3-3',
        team2_formation: formData.get('team2_formation') || '4-3-3'
    };

    const result = await api.post('/matches/add', matchData);
    if (result.ok) {
        showFlash('Матч успішно створено!', 'success');
        event.target.reset();
        loadMatches(); // Reload matches list
    } else {
        showFlash(result.result.message || 'Помилка створення матчу', 'danger');
    }
}

// Load match data
async function loadMatchData(matchId) {
    currentMatchId = matchId;

    // Get match data
    const pageData = await api.get('/matches-page', { matches: [], teams: [] });
    const match = pageData.matches.find(m => m.id === matchId);
    if (!match) return;

    // Get votes
    const votesData = await api.get(`/votes/${matchId}`, { votes: [] });
    const votesMap = {};
    (votesData.votes || []).forEach(v => {
        votesMap[v.player_id] = v.votes;
    });

    // Get players
    const playersData = await api.get('/players', { players: [] });
    const allPlayers = playersData.players || [];

    // Build rosters
    const homeTeam = pageData.teams.find(t => t.name === match.team1);
    const awayTeam = pageData.teams.find(t => t.name === match.team2);

    const homePlayers = allPlayers.filter(p => p.team_id === homeTeam?.id);
    const awayPlayers = allPlayers.filter(p => p.team_id === awayTeam?.id);

    // Get formations for teams (from match data or UI, default to 4-3-3)
    const homeFormationSelect = document.getElementById('home-formation');
    const awayFormationSelect = document.getElementById('away-formation');
    const homeFormation = match.team1_formation || match.home_formation || homeFormationSelect?.value || defaultFormation;
    const awayFormation = match.team2_formation || match.away_formation || awayFormationSelect?.value || defaultFormation;

    // Set formation selectors
    if (homeFormationSelect) homeFormationSelect.value = homeFormation;
    if (awayFormationSelect) awayFormationSelect.value = awayFormation;

    // Show formation controls
    const formationControls = document.getElementById('formation-controls');
    if (formationControls) formationControls.style.display = 'block';

    // Build rosters with formations
    const homeRoster = buildRosterByFormation(homePlayers, votesMap, 'home', homeFormation);
    const awayRoster = buildRosterByFormation(awayPlayers, votesMap, 'away', awayFormation);

    // Update UI
    updateScoreboard(match, homeRoster, awayRoster);
    renderPitch(homeRoster, awayRoster, match);
    renderStats(homeRoster, awayRoster, match);

    document.getElementById('pitch-section').style.display = 'block';

    // Add event listeners for formation changes
    if (homeFormationSelect) {
        // Remove old listener if exists
        const newHomeSelect = homeFormationSelect.cloneNode(true);
        homeFormationSelect.parentNode.replaceChild(newHomeSelect, homeFormationSelect);
        newHomeSelect.onchange = () => {
            const newFormation = newHomeSelect.value;
            const newRoster = buildRosterByFormation(homePlayers, votesMap, 'home', newFormation);
            renderPitch(newRoster, awayRoster, match);
            renderStats(newRoster, awayRoster, match);
            updateScoreboard(match, newRoster, awayRoster);
        };
    }

    if (awayFormationSelect) {
        // Remove old listener if exists
        const newAwaySelect = awayFormationSelect.cloneNode(true);
        awayFormationSelect.parentNode.replaceChild(newAwaySelect, awayFormationSelect);
        newAwaySelect.onchange = () => {
            const newFormation = newAwaySelect.value;
            const newRoster = buildRosterByFormation(awayPlayers, votesMap, 'away', newFormation);
            renderPitch(homeRoster, newRoster, match);
            renderStats(homeRoster, newRoster, match);
            updateScoreboard(match, homeRoster, newRoster);
        };
    }
}

// Build roster using formation scheme
function buildRosterByFormation(players, votesMap, side, formationName) {
    if (!players || players.length === 0) {
        return [];
    }

    // Get formation or use default
    const formation = formations[formationName] || formations[defaultFormation];
    if (!formation || !formation.positions) {
        console.warn(`Formation ${formationName} not found, using default`);
        return buildRoster(players, votesMap, side);
    }

    // Group players by position
    const playersByPos = {};
    players.forEach(player => {
        const pos = (player.position || 'CM').toUpperCase();
        if (!playersByPos[pos]) {
            playersByPos[pos] = [];
        }
        playersByPos[pos].push(player);
    });

    // Map formation positions to players
    const roster = [];
    const usedPlayers = new Set();

    // First pass: match exact positions
    formation.positions.forEach((formPos, index) => {
        const posKey = formPos.pos.toUpperCase();
        const candidates = playersByPos[posKey] || [];

        if (candidates.length > 0) {
            // Find best match (not used yet)
            const player = candidates.find(p => !usedPlayers.has(p.id)) || candidates[0];
            if (player && !usedPlayers.has(player.id)) {
                usedPlayers.add(player.id);
                roster.push({
                    ...player,
                    x: formPos.x,
                    y: formPos.y,
                    formationIndex: index,
                    votes: votesMap[player.id] || 0,
                    short_name: player.name.split(' ').pop() || player.name
                });
            }
        }
    });

    // Second pass: fill remaining positions with closest matches
    const remainingPlayers = players.filter(p => !usedPlayers.has(p.id));
    if (remainingPlayers.length > 0 && roster.length < formation.positions.length) {
        const emptySlots = formation.positions.filter((_, idx) =>
            !roster.some(r => r.formationIndex === idx)
        );

        remainingPlayers.forEach(player => {
            if (emptySlots.length === 0) return;

            // Find closest position match
            const playerPos = (player.position || 'CM').toUpperCase();
            let bestSlot = emptySlots[0];
            let bestScore = Infinity;

            emptySlots.forEach(slot => {
                const slotPos = slot.pos.toUpperCase();
                // Calculate similarity score
                let score = 100;
                if (playerPos === slotPos) score = 0;
                else if (playerPos.includes(slotPos) || slotPos.includes(playerPos)) score = 10;
                else if (isCompatiblePosition(playerPos, slotPos)) score = 20;
                else score = 50;

                if (score < bestScore) {
                    bestScore = score;
                    bestSlot = slot;
                }
            });

            const slotIndex = emptySlots.indexOf(bestSlot);
            if (slotIndex >= 0) {
                emptySlots.splice(slotIndex, 1);
                roster.push({
                    ...player,
                    x: bestSlot.x,
                    y: bestSlot.y,
                    formationIndex: formation.positions.indexOf(bestSlot),
                    votes: votesMap[player.id] || 0,
                    short_name: player.name.split(' ').pop() || player.name
                });
            }
        });
    }

    // Apply side mirroring and bounds
    return roster.map(player => {
        const x = side === 'home' ? player.x : 100 - player.x;
        const y = side === 'home' ? player.y : 100 - player.y;

        return {
            ...player,
            x: Math.max(1, Math.min(99, x)),
            y: Math.max(2, Math.min(98, y))
        };
    });
}

// Check if positions are compatible (e.g., CM can play CAM)
function isCompatiblePosition(playerPos, slotPos) {
    const compatibility = {
        'GK': ['GK'],
        'CB': ['CB', 'LCB', 'RCB'],
        'LB': ['LB', 'LWB'],
        'RB': ['RB', 'RWB'],
        'CDM': ['CDM', 'CM'],
        'CM': ['CM', 'CDM', 'CAM', 'LCM', 'RCM'],
        'CAM': ['CAM', 'CM', 'LW', 'RW'],
        'LM': ['LM', 'LW', 'CM'],
        'RM': ['RM', 'RW', 'CM'],
        'LW': ['LW', 'LM', 'LF', 'CAM'],
        'RW': ['RW', 'RM', 'RF', 'CAM'],
        'ST': ['ST', 'CF', 'LS', 'RS'],
        'CF': ['CF', 'ST', 'CAM']
    };

    const compatible = compatibility[playerPos] || [];
    return compatible.includes(slotPos) || slotPos === playerPos;
}

// Build roster with positions
function buildRoster(players, votesMap, side) {
    if (!players || players.length === 0) {
        return [];
    }

    // Sort players by position for better distribution
    const positionOrder = {
        'GK': 0, 'CB': 1, 'LCB': 2, 'RCB': 3, 'LB': 4, 'RB': 5, 'LWB': 6, 'RWB': 7,
        'CDM': 8, 'LDM': 9, 'RDM': 10, 'CM': 11, 'LCM': 12, 'RCM': 13, 'LM': 14, 'RM': 15,
        'CAM': 16, 'LAM': 17, 'RAM': 18, 'LW': 19, 'RW': 20, 'LF': 21, 'RF': 22,
        'ST': 23, 'CF': 24, 'LS': 25, 'RS': 26
    };

    const sortedPlayers = [...players].sort((a, b) => {
        const aPos = (a.position || 'CM').toUpperCase();
        const bPos = (b.position || 'CM').toUpperCase();
        const aOrder = positionOrder[aPos] ?? 99;
        const bOrder = positionOrder[bPos] ?? 99;
        if (aOrder !== bOrder) return aOrder - bOrder;
        // If same position, sort by name for consistency
        return (a.name || '').localeCompare(b.name || '');
    });

    // Group players by position to avoid overlapping
    const positionGroups = {};
    sortedPlayers.forEach(player => {
        const pos = (player.position || 'CM').toUpperCase();
        if (!positionGroups[pos]) {
            positionGroups[pos] = [];
        }
        positionGroups[pos].push(player);
    });

    return sortedPlayers.map((player, globalIndex) => {
        const posKey = (player.position || 'CM').toUpperCase();
        const pos = positionMap[posKey] || { x: 50, y: 50 };

        // Calculate base position
        let baseX = pos.x;
        let baseY = pos.y;

        // Add offset for multiple players in same position to avoid overlap
        const samePositionPlayers = positionGroups[posKey] || [];
        const playerIndex = samePositionPlayers.indexOf(player);
        if (samePositionPlayers.length > 1) {
            // For defenders and forwards, spread horizontally
            // For midfielders and wingers, spread vertically
            const isCentral = ['GK', 'CB', 'LCB', 'RCB', 'CDM', 'CM', 'CAM', 'ST', 'CF'].includes(posKey);
            const isWide = ['LB', 'RB', 'LWB', 'RWB', 'LM', 'RM', 'LW', 'RW', 'LF', 'RF', 'LS', 'RS'].includes(posKey);

            if (isCentral) {
                // Spread horizontally (left-right)
                const spacing = Math.min(6, 30 / samePositionPlayers.length);
                const offset = (playerIndex - (samePositionPlayers.length - 1) / 2) * spacing;
                baseX += offset;
            } else if (isWide) {
                // Spread vertically (up-down) but keep within reasonable bounds
                const spacing = Math.min(8, 40 / samePositionPlayers.length);
                const offset = (playerIndex - (samePositionPlayers.length - 1) / 2) * spacing;
                baseY += offset;
            } else {
                // Default: spread vertically
                const spacing = Math.min(8, 40 / samePositionPlayers.length);
                const offset = (playerIndex - (samePositionPlayers.length - 1) / 2) * spacing;
                baseY += offset;
            }
        }

        // Apply side (home = left side, away = right side)
        // For home team: use positions as-is (left side)
        // For away team: mirror horizontally (right side)
        const x = side === 'home' ? baseX : 100 - baseX;
        const y = side === 'home' ? baseY : 100 - baseY;

        // Ensure positions are within field bounds
        const finalX = Math.max(1, Math.min(99, x));
        const finalY = Math.max(2, Math.min(98, y));

        return {
            ...player,
            x: finalX,
            y: finalY,
            votes: votesMap[player.id] || 0,
            short_name: player.name.split(' ').pop() || player.name
        };
    });
}

// Update scoreboard
function updateScoreboard(match, homeRoster, awayRoster) {
    const homeTotal = homeRoster.reduce((sum, p) => sum + p.votes, 0);
    const awayTotal = awayRoster.reduce((sum, p) => sum + p.votes, 0);

    const team1Name = match.team1 || 'Господарі';
    const team2Name = match.team2 || 'Гості';

    document.getElementById('scoreboard').innerHTML = `
        <div class="score-row">
            <div class="score-item">
                <span class="score-label">${team1Name}</span>
                <span class="score-val">${homeTotal}</span>
            </div>
            <div class="score-item">
                <span class="score-label">VS</span>
            </div>
            <div class="score-item">
                <span class="score-label">${team2Name}</span>
                <span class="score-val">${awayTotal}</span>
            </div>
        </div>
    `;

    document.getElementById('home-label').innerHTML = `
        <div class="dot" style="width: 12px; height: 12px; background: #ef4444; border-radius: 50%; display: inline-block; margin-right: 8px;"></div>
        <span>${team1Name}</span>
    `;

    document.getElementById('away-label').innerHTML = `
        <span>${team2Name}</span>
        <div class="dot" style="width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; display: inline-block; margin-left: 8px;"></div>
    `;
}

// Render pitch
function renderPitch(homeRoster, awayRoster, match) {
    const pitch = document.getElementById('pitch');
    const existingPlayers = pitch.querySelectorAll('.player-dot');
    existingPlayers.forEach(p => p.remove());

    homeRoster.forEach(player => {
        const btn = createPlayerButton(player, 'home', match.team1);
        pitch.appendChild(btn);
    });

    awayRoster.forEach(player => {
        const btn = createPlayerButton(player, 'away', match.team2);
        pitch.appendChild(btn);
    });
}

// Create player button
function createPlayerButton(player, side, teamName) {
    const btn = document.createElement('button');
    btn.className = `player-dot ${side}`;
    btn.style.top = `${player.y}%`;
    btn.style.left = `${player.x}%`;
    btn.title = player.name;
    btn.innerHTML = `
        ${player.number || ''}
        <span class="player-name-visible">${player.short_name}</span>
        <div class="player-info">
            <span class="player-name">${player.name}</span>
            <span class="player-position">${player.position}</span>
            <span class="player-votes">★ ${player.votes}</span>
        </div>
    `;

    if (!userHasVoted) {
        btn.onclick = () => openPlayerModal(player, teamName, side);
    } else {
        btn.disabled = true;
    }

    return btn;
}

// Open player modal
function openPlayerModal(player, teamName, side) {
    if (userHasVoted) {
        alert('Ви вже проголосували в цьому матчі.');
        return;
    }

    document.getElementById('modalPlayerName').textContent = player.name;
    document.getElementById('modalPlayerPosition').textContent = player.position;
    document.getElementById('modalPlayerVotes').textContent = player.votes;
    document.getElementById('modalPlayerTeamName').textContent = teamName;
    document.getElementById('modalPlayerNumber').textContent = player.number || '';

    document.getElementById('vote-section').innerHTML = `
        <form id="voteForm" onsubmit="submitVote(event, ${player.id})">
            <button type="submit" class="btn btn-primary btn-vote" style="width: 100%;">
                Проголосувати за цього гравця
            </button>
        </form>
    `;

    document.getElementById('playerModal').style.display = 'block';
}

// Submit vote
async function submitVote(event, playerId) {
    event.preventDefault();
    if (!currentMatchId) return;

    const result = await api.post('/vote', {
        player_id: playerId,
        match_id: currentMatchId
    });

    if (result.ok) {
        showFlash('Голос зараховано!', 'success');
        document.getElementById('playerModal').style.display = 'none';
        userHasVoted = true;
        loadMatchData(currentMatchId); // Reload
    } else {
        showFlash(result.result.message || 'Помилка голосування', 'danger');
    }
}

// Render stats
function renderStats(homeRoster, awayRoster, match) {
    const maxVotes = Math.max(
        ...homeRoster.map(p => p.votes),
        ...awayRoster.map(p => p.votes),
        1
    );

    const team1Name = match.team1 || 'Господарі';
    const team2Name = match.team2 || 'Гості';
    document.getElementById('home-team-name').textContent = `${team1Name} - Рейтинг`;
    document.getElementById('away-team-name').textContent = `${team2Name} - Рейтинг`;

    const homeStats = homeRoster
        .sort((a, b) => b.votes - a.votes)
        .map(p => `
            <div class="stat-row">
                <div class="stat-info">
                    <span class="stat-name">${p.short_name}</span>
                    <span class="stat-votes">${p.votes}</span>
                </div>
                <div class="stat-bar-bg">
                    <div class="stat-bar-fill home" style="width: ${(p.votes / maxVotes) * 100}%;"></div>
                </div>
            </div>
        `).join('');

    const awayStats = awayRoster
        .sort((a, b) => b.votes - a.votes)
        .map(p => `
            <div class="stat-row">
                <div class="stat-info">
                    <span class="stat-name">${p.short_name}</span>
                    <span class="stat-votes">${p.votes}</span>
                </div>
                <div class="stat-bar-bg">
                    <div class="stat-bar-fill away" style="width: ${(p.votes / maxVotes) * 100}%;"></div>
                </div>
            </div>
        `).join('');

    document.getElementById('home-stats').innerHTML = homeStats;
    document.getElementById('away-stats').innerHTML = awayStats;
}

// Close modal
document.querySelector('.modal-close')?.addEventListener('click', () => {
    document.getElementById('playerModal').style.display = 'none';
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadMatches();
});


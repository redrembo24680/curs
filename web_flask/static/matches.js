// Matches page functionality
let currentMatchId = null;
let userVotedPlayerIds = []; // Global list of players user voted for

// User login status (will be set by checkUserLoginStatus)
window.userLoggedIn = false;
window.currentUser = null;

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
    const playersData = await api.get('/players', { players: [] });
    const players = playersData.players || [];

    // Show all matches - don't filter aggressively
    // We'll just handle empty rosters when loading match data
    const validMatches = matches;

    // Check user login status and update UI
    await checkUserLoginStatus();
    updateAuthBar();

    const select = document.getElementById('match-select');

    // Load teams for admin form
    const team1Select = document.getElementById('create-team1');
    const team2Select = document.getElementById('create-team2');
    if (team1Select && team2Select && teams.length > 0) {
        const teamOptions = teams.map(t => `<option value="${t.name}">${t.name}</option>`).join('');
        team1Select.innerHTML = '<option value="">Оберіть команду...</option>' + teamOptions;
        team2Select.innerHTML = '<option value="">Оберіть команду...</option>' + teamOptions;
    }

    // Check if user is admin and show admin form
    const adminForm = document.getElementById('admin-match-form');
    if (adminForm) {
        if (window.currentUser && window.currentUser.role === 'admin') {
            adminForm.style.display = 'block';
        } else {
            adminForm.style.display = 'none';
        }
    }

    if (validMatches.length === 0) {
        select.innerHTML = '<option value="">Немає матчів</option>';
        return;
    }

    select.innerHTML = '<option value="">Оберіть матч...</option>' +
        validMatches.map(m => `<option value="${m.id}">${m.team1} vs ${m.team2} - ${m.isActive ? 'Активний' : 'Завершено'}</option>`).join('');

    select.addEventListener('change', (e) => {
        if (e.target.value) {
            loadMatchData(parseInt(e.target.value));
        } else {
            document.getElementById('pitch-section').style.display = 'none';
        }
    });

    // Auto-select first match
    if (validMatches.length > 0 && validMatches[0].isActive) {
        select.value = validMatches[0].id;
        loadMatchData(validMatches[0].id);
    }
}

// Handle match creation
async function handleCreateMatch(event) {
    event.preventDefault();

    // Check if user is admin
    if (!window.currentUser || window.currentUser.role !== 'admin') {
        showFlash('Тільки адміністратори можуть створювати матчі', 'danger');
        return;
    }

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

// Authentication removed - no login checks needed

// Check user login status
async function checkUserLoginStatus() {
    try {
        const response = await fetch('/api/user-info', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const userInfo = await response.json();
        window.userLoggedIn = userInfo.logged_in || false;
        window.currentUser = userInfo.logged_in ? userInfo : null;

        // If user is logged in, load their global vote history (all players they voted for)
        if (window.userLoggedIn) {
            try {
                const votesResponse = await fetch('/api/user-player-votes', {
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                if (votesResponse.ok) {
                    const votesData = await votesResponse.json();
                    userVotedPlayerIds = votesData.player_ids || [];
                }
            } catch (e) {
                console.warn('Could not load user vote history:', e);
            }
        } else {
            userVotedPlayerIds = [];
        }
    } catch (error) {
        console.error('Error checking login status:', error);
        window.userLoggedIn = false;
        window.currentUser = null;
        userVotedPlayerIds = [];
    }
}

// Check if user has voted for current match
async function checkUserVoteStatus(matchId) {
    if (!window.userLoggedIn) {
        userHasVoted = false;
        votedPlayerId = null;
        userVotedPlayerIds = [];
        return;
    }

    let lastError = null;
    for (let attempt = 0; attempt < 2; attempt++) {
        try {
            const response = await fetch(`/api/vote-status/${matchId}`, {
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                if (attempt === 0) {
                    await new Promise(r => setTimeout(r, 300)); // Wait before retry
                    continue;
                }
                throw new Error(`HTTP ${response.status}`);
            }

            const status = await response.json();
            userHasVoted = status.has_voted || false;

            // Update list of players user voted for
            if (status.player_ids && Array.isArray(status.player_ids)) {
                userVotedPlayerIds = status.player_ids;
            } else {
                userVotedPlayerIds = [];
            }

            if (status.has_voted && status.player_id) {
                votedPlayerId = status.player_id;
            } else {
                votedPlayerId = null;
            }
            return; // Success - exit retry loop
        } catch (error) {
            lastError = error;
            if (attempt === 0) {
                await new Promise(r => setTimeout(r, 300)); // Wait before retry
                continue;
            }
        }
    }

    // If all retries failed
    console.warn('Could not load vote status:', lastError);
    userHasVoted = false;
    votedPlayerId = null;
}

// Update auth bar with user info
async function updateAuthBar() {
    const authBar = document.getElementById('auth-bar');
    if (!authBar) return;

    try {
        const response = await fetch('/api/user-info', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const userInfo = await response.json();

        if (userInfo.logged_in) {
            authBar.innerHTML = `
                <span class="user-pill" style="margin-right: 0.5rem; padding: 0.5rem 1rem; background: #f3f4f6; border-radius: 20px; font-size: 0.9rem;">
                    ${userInfo.username || 'Користувач'}
                    ${userInfo.role === 'admin' ? '<small style="margin-left: 0.5rem; padding: 0.2rem 0.5rem; background: #10b981; color: white; border-radius: 10px; font-size: 0.75rem;">Admin</small>' : ''}
                </span>
                <a class="btn ghost" href="/logout">Вийти</a>
            `;
        } else {
            authBar.innerHTML = `
                <a class="btn ghost" href="/login">Увійти</a>
                <a class="btn primary small" href="/register">Реєстрація</a>
            `;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        authBar.innerHTML = `
            <a class="btn ghost" href="/login">Увійти</a>
            <a class="btn primary small" href="/register">Реєстрація</a>
        `;
    }
}

// Load match data
async function loadMatchData(matchId) {
    currentMatchId = matchId;

    // Check user login and vote status FIRST
    await checkUserLoginStatus();
    await checkUserVoteStatus(matchId);

    // Reset vote status if match changed
    if (currentMatchId !== matchId) {
        userHasVoted = false;
        votedPlayerId = null;
    }

    // Get match data
    const pageData = await api.get('/matches-page', { matches: [], teams: [] });
    const match = pageData.matches.find(m => m.id === matchId);
    if (!match) return;

    // Get votes from Flask DB (fast, local - not from C++ API)
    const votesData = await fetch(`/api/match-votes/${matchId}`).then(r => r.json()).catch(() => ({ votes: [] }));
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

    const homePlayers = homeTeam ? allPlayers.filter(p => p.team_id === homeTeam.id) : [];
    const awayPlayers = awayTeam ? allPlayers.filter(p => p.team_id === awayTeam.id) : [];

    // Get formations for teams (ONLY from match data, static - cannot be changed)
    const homeFormation = match.team1_formation || match.home_formation || defaultFormation;
    const awayFormation = match.team2_formation || match.away_formation || defaultFormation;

    // Update formation display (read-only, show as text)
    const homeFormationSelect = document.getElementById('home-formation');
    const awayFormationSelect = document.getElementById('away-formation');
    if (homeFormationSelect) {
        homeFormationSelect.value = homeFormation;
        homeFormationSelect.disabled = true; // Make it read-only
        homeFormationSelect.style.backgroundColor = '#f3f4f6';
        homeFormationSelect.style.cursor = 'not-allowed';
    }
    if (awayFormationSelect) {
        awayFormationSelect.value = awayFormation;
        awayFormationSelect.disabled = true; // Make it read-only
        awayFormationSelect.style.backgroundColor = '#f3f4f6';
        awayFormationSelect.style.cursor = 'not-allowed';
    }

    // Show formation controls (but they are disabled)
    const formationControls = document.getElementById('formation-controls');
    if (formationControls) {
        formationControls.style.display = 'block';
        // Add note that formations are fixed
        const note = formationControls.querySelector('.formation-note');
        if (!note) {
            const noteDiv = document.createElement('div');
            noteDiv.className = 'formation-note';
            noteDiv.style.cssText = 'grid-column: 1 / -1; padding: 0.5rem; background: #fef3c7; border-radius: 6px; font-size: 0.875rem; color: #92400e; text-align: center; margin-top: 0.5rem;';
            noteDiv.textContent = 'ℹ️ Схеми команд встановлені при створенні матчу і не можуть бути змінені';
            formationControls.querySelector('.card').appendChild(noteDiv);
        }
    }

    // Build rosters with formations (static, from match data)
    const homeRoster = buildRosterByFormation(homePlayers, votesMap, 'home', homeFormation);
    const awayRoster = buildRosterByFormation(awayPlayers, votesMap, 'away', awayFormation);

    // Update UI
    updateScoreboard(match, homeRoster, awayRoster);
    renderPitch(homeRoster, awayRoster, match);
    renderStats(homeRoster, awayRoster, match);

    document.getElementById('pitch-section').style.display = 'block';

    // Load comments for this match
    loadComments(matchId);

    // Setup comment form
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        // Remove old listeners
        const newForm = commentForm.cloneNode(true);
        commentForm.parentNode.replaceChild(newForm, commentForm);
        newForm.onsubmit = (e) => addComment(e, matchId);
    }

    // NO event listeners for formation changes - formations are static!
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
        const btn = createPlayerButton(player, 'home', match.team1, match.isActive);
        pitch.appendChild(btn);
    });

    awayRoster.forEach(player => {
        const btn = createPlayerButton(player, 'away', match.team2, match.isActive);
        pitch.appendChild(btn);
    });
}

// Create player button
function createPlayerButton(player, side, teamName, matchIsActive = true) {
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

    // Check if match is closed
    if (!matchIsActive) {
        btn.disabled = true;
        btn.style.cursor = 'not-allowed';
        btn.style.opacity = '0.5';
        btn.title = 'Матч закрито, голосування недоступне';
        btn.onclick = () => {
            showFlash('Цей матч закрито, голосування недоступне', 'warning');
        };
    }
    // Only allow clicking if user is logged in and hasn't voted
    else if (window.userLoggedIn && !userHasVoted) {
        btn.onclick = () => openPlayerModal(player, teamName, side);
        btn.style.cursor = 'pointer';
        btn.title = `${player.name} (${player.position}) - ${player.votes} голосів`;
    } else if (!window.userLoggedIn) {
        btn.onclick = () => {
            showFlash('Для голосування потрібно увійти до системи', 'warning');
            setTimeout(() => window.location.href = '/login', 1500);
        };
        btn.style.cursor = 'pointer';
        btn.title = 'Увійдіть для голосування';
    } else {
        // User has already voted
        btn.disabled = true;
        btn.style.cursor = 'not-allowed';
        btn.style.opacity = '0.6';
        if (votedPlayerId === player.id) {
            btn.title = 'Ви проголосували за цього гравця';
            btn.style.border = '2px solid #10b981';
            btn.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.5)';
        } else {
            btn.title = 'Ви вже проголосували в цьому матчі';
        }
    }

    return btn;
}

// Open player modal
function openPlayerModal(player, teamName, side) {
    // Check if user is logged in
    if (!window.userLoggedIn) {
        alert('Для голосування потрібно увійти до системи. Перейдіть на сторінку входу.');
        window.location.href = '/login';
        return;
    }

    // Check if user already voted for THIS SPECIFIC PLAYER
    if (userVotedPlayerIds && userVotedPlayerIds.includes(player.id)) {
        showFlash('Ви вже проголосували за цього гравця', 'warning');
        return;
    }

    document.getElementById('modalPlayerName').textContent = player.name;
    document.getElementById('modalPlayerPosition').textContent = player.position;
    document.getElementById('modalPlayerVotes').textContent = player.votes;
    document.getElementById('modalPlayerTeamName').textContent = teamName;
    document.getElementById('modalPlayerNumber').textContent = player.number || '';

    document.getElementById('vote-section').innerHTML = `
        <form id="voteForm" onsubmit="submitVote(event, ${player.id})">
            <button type="submit" id="voteButton" class="btn btn-primary btn-vote" style="width: 100%;">
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

    // Check if user is logged in
    if (!window.userLoggedIn) {
        showFlash('Для голосування потрібно увійти до системи', 'danger');
        window.location.href = '/login';
        return;
    }

    // Get and disable vote button
    const voteButton = document.getElementById('voteButton');
    if (voteButton) {
        voteButton.disabled = true;
        voteButton.textContent = 'Завантаження...';
    }

    // Use Flask endpoint which checks authentication
    try {
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin', // Include cookies for session
            body: JSON.stringify({
                player_id: playerId,
                match_id: currentMatchId
            })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            showFlash('✓ Голос успішно зараховано!', 'success');
            document.getElementById('playerModal').style.display = 'none';

            // Add player to voted list
            if (!userVotedPlayerIds.includes(playerId)) {
                userVotedPlayerIds.push(playerId);
            }

            userHasVoted = true;
            votedPlayerId = playerId;

            // Log vote for diagnostics
            console.log(`Vote submitted: player ${playerId} in match ${currentMatchId}`);

            // Reload match data after a delay to get updated votes from C++ API
            // Use 1.5s delay to ensure backend processing is complete
            setTimeout(() => {
                console.log('Reloading match data...');
                loadMatchData(currentMatchId).catch(e => console.error('Error reloading match:', e));
            }, 1500);
        } else {
            const errorMsg = result.message || 'Помилка голосування';
            showFlash(errorMsg, 'danger');

            // Re-enable button on error
            if (voteButton) {
                voteButton.disabled = false;
                voteButton.textContent = 'Проголосувати за цього гравця';
            }

            // If user already voted, update status
            if (errorMsg.includes('вже проголосували') || result.has_voted) {
                userHasVoted = true;
                if (result.player_id) {
                    votedPlayerId = result.player_id;
                }
                // Don't reload - user already voted message is enough
            }

            if (errorMsg.includes('увійти') || response.status === 401) {
                setTimeout(() => window.location.href = '/login', 2000);
            }
        }
    } catch (error) {
        showFlash('Помилка підключення до сервера', 'danger');
        console.error('Vote error:', error);

        // Re-enable button on error
        if (voteButton) {
            voteButton.disabled = false;
            voteButton.textContent = 'Проголосувати за цього гравця';
        }
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

// Load comments for match
async function loadComments(matchId) {
    if (!matchId) return;

    try {
        const response = await fetch(`/api/matches/${matchId}/comments`);
        const data = await response.json();
        const comments = data.comments || [];
        const commentsDiv = document.getElementById('comments-container');

        if (!commentsDiv) return;

        if (comments.length === 0) {
            commentsDiv.innerHTML = '<p class="muted">Коментарів ще немає. Будьте першим!</p>';
        } else {
            commentsDiv.innerHTML = comments.map(comment => `
                <div style="padding: 1rem; margin-bottom: 1rem; background: #f9fafb; border-radius: 8px; border-left: 3px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <strong>${comment.username || 'Користувач'}</strong>
                            <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">
                                ${new Date(comment.created_at).toLocaleString('uk-UA')}
                            </span>
                        </div>
                        ${comment.is_own ? `
                            <button class="btn ghost small" onclick="deleteComment(${comment.id})" style="color: #ef4444; font-size: 0.75rem;">Видалити</button>
                        ` : ''}
                    </div>
                    <p style="margin: 0; white-space: pre-wrap;">${comment.comment_text}</p>
                </div>
            `).join('');
        }

        // Show/hide comment form based on login status
        const commentForm = document.getElementById('add-comment-form');
        if (commentForm) {
            if (window.userLoggedIn) {
                commentForm.style.display = 'block';
            } else {
                commentForm.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error loading comments:', error);
        const commentsDiv = document.getElementById('comments-container');
        if (commentsDiv) {
            commentsDiv.innerHTML = '<p class="muted">Помилка завантаження коментарів.</p>';
        }
    }
}

// Add comment
async function addComment(event, matchId) {
    event.preventDefault();

    if (!window.userLoggedIn) {
        showFlash('Для додавання коментарів потрібно увійти до системи', 'warning');
        window.location.href = '/login';
        return;
    }

    const formData = new FormData(event.target);
    const commentText = formData.get('comment_text').trim();

    if (!commentText) {
        showFlash('Введіть текст коментаря', 'warning');
        return;
    }

    try {
        const response = await fetch(`/api/matches/${matchId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ comment_text: commentText })
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            showFlash('Коментар додано!', 'success');
            event.target.reset();
            loadComments(matchId);
        } else {
            showFlash(result.error || 'Помилка додавання коментаря', 'danger');
        }
    } catch (error) {
        showFlash('Помилка підключення до сервера', 'danger');
        console.error('Add comment error:', error);
    }
}

// Delete comment
async function deleteComment(commentId) {
    if (!confirm('Ви впевнені, що хочете видалити цей коментар?')) {
        return;
    }

    try {
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            showFlash('Коментар видалено', 'success');
            if (currentMatchId) {
                loadComments(currentMatchId);
            }
        } else {
            showFlash(result.error || 'Помилка видалення', 'danger');
        }
    } catch (error) {
        showFlash('Помилка підключення до сервера', 'danger');
        console.error('Delete comment error:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Check user login status first
    await checkUserLoginStatus();
    // Update auth bar
    updateAuthBar();
    // Load matches
    loadMatches();
});


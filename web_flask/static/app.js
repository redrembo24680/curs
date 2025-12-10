// API Configuration
const API_BASE_URL = 'http://localhost:8080/api';

// API Client
class APIClient {
    async get(endpoint, defaultData = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) {
                console.error(`API GET ${endpoint} failed: ${response.status}`);
                return defaultData;
            }
            return await response.json();
        } catch (error) {
            console.error(`API GET ${endpoint} error:`, error);
            return defaultData;
        }
    }

    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const error = await response.json();
                return { ok: false, result: error };
            }
            return { ok: true, result: await response.json() };
        } catch (error) {
            console.error(`API POST ${endpoint} error:`, error);
            return { ok: false, result: { message: error.message } };
        }
    }
}

const api = new APIClient();

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showFlash(message, type = 'info') {
    const flashContainer = document.getElementById('flash-container');
    if (!flashContainer) return;

    const flash = document.createElement('div');
    flash.className = `flash flash-${type}`;
    flash.textContent = message;
    flashContainer.appendChild(flash);

    setTimeout(() => flash.remove(), 5000);
}

// Load global stats
async function loadGlobalStats() {
    // Try to get stats from Flask local DB first (fast)
    let stats;
    try {
        const response = await fetch('/api/flask-stats', {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json' }
        });
        if (response.ok) {
            stats = await response.json();
        } else {
            // Fallback to C++ API
            stats = await api.get('/stats', { total_players: 0, total_matches: 0, total_votes: 0 });
        }
    } catch (err) {
        console.log('Could not fetch Flask stats, trying C++ API', err);
        stats = await api.get('/stats', { total_players: 0, total_matches: 0, total_votes: 0 });
    }

    const statsBar = document.getElementById('stats-bar');
    if (statsBar) {
        statsBar.innerHTML = `
            <span>👥 ${stats.total_players || 0} гравців</span>
            <span>🏟️ ${stats.total_matches || 0} матчів</span>
            <span>🗳️ ${stats.total_votes || 0} голосів</span>
        `;
    }
}

// Load user info
async function loadUserInfo() {
    const authBar = document.getElementById('auth-bar');
    const loginTip = document.getElementById('login-tip');

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
            // User is logged in - update auth bar
            if (authBar) {
                authBar.innerHTML = `
                    <span class="user-pill" style="margin-right: 0.5rem; padding: 0.5rem 1rem; background: #f3f4f6; border-radius: 20px; font-size: 0.9rem;">
                        ${userInfo.username || 'Користувач'}
                        ${userInfo.role === 'admin' ? '<small style="margin-left: 0.5rem; padding: 0.2rem 0.5rem; background: #10b981; color: white; border-radius: 10px; font-size: 0.75rem;">Admin</small>' : ''}
                    </span>
                    <a class="btn ghost" href="/logout">Вийти</a>
                `;
            }
            // Hide login tip if user is logged in
            if (loginTip) {
                loginTip.style.display = 'none';
            }
        } else {
            // User is not logged in
            if (authBar) {
                authBar.innerHTML = `
                    <a class="btn ghost" href="/login">Увійти</a>
                    <a class="btn primary small" href="/register">Реєстрація</a>
                `;
            }
            // Show login tip if user is not logged in
            if (loginTip) {
                loginTip.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        if (authBar) {
            authBar.innerHTML = `
                <a class="btn ghost" href="/login">Увійти</a>
                <a class="btn primary small" href="/register">Реєстрація</a>
            `;
        }
        // Show login tip on error
        if (loginTip) {
            loginTip.style.display = 'block';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGlobalStats();
    loadUserInfo();

    // Set active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath ||
            (currentPath === '/' && link.getAttribute('href') === '/index.html')) {
            link.classList.add('active');
        }
    });
});

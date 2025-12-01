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
    const stats = await api.get('/stats', { total_players: 0, total_matches: 0, total_votes: 0 });
    const statsBar = document.getElementById('stats-bar');
    if (statsBar) {
        statsBar.innerHTML = `
            <span>👥 ${stats.total_players || 0} гравців</span>
            <span>🏟️ ${stats.total_matches || 0} матчів</span>
            <span>🗳️ ${stats.total_votes || 0} голосів</span>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadGlobalStats();
    
    // Set active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath === '/' && link.getAttribute('href') === '/index.html')) {
            link.classList.add('active');
        }
    });
});


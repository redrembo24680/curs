"""Stats routes."""
from flask import Blueprint, send_from_directory, jsonify
import os
from utils.api_client import _get

bp = Blueprint('stats', __name__)


@bp.route("/stats")
def stats():
    """Stats page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'stats.html')


@bp.route("/api/stats-page")
def stats_page():
    """Get statistics for stats page from C++ backend API."""
    try:
        # Get data from C++ backend
        stats_data = _get("/api/stats")
        
        if not stats_data:
            return jsonify({"error": "Failed to fetch stats from backend"}), 500
        
        # Get players data
        players_data = _get("/api/players")
        if not players_data:
            players_list = []
        else:
            # Sort players by votes
            players = players_data.get("players", [])
            players_list = sorted(players, key=lambda p: p.get("votes", 0), reverse=True)[:20]
        
        # Get matches data with full statistics
        matches_data = _get("/api/match-stats")
        matches_list = matches_data.get("matches", []) if matches_data else []
        
        return jsonify({
            "top_players": players_list,
            "matches": matches_list,
            "stats": stats_data
        })

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting stats page data: {e}")
        return jsonify({
            "top_players": [],
            "matches": [],
            "stats": {}
        }), 500

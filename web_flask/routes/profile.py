"""Profile routes."""
from flask import Blueprint, send_file, request, jsonify, session, g
import os
import requests
from utils.decorators import login_required
from utils.database import get_db
from utils.api_client import API_BASE_URL

bp = Blueprint('profile', __name__)


@bp.route("/profile")
@login_required
def profile():
    """User profile page - show voting history."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'profile.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/api/profile/votes")
@login_required
def get_user_votes():
    """Get user's voting history."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    db = get_db()
    try:
        # Get all votes by user from Flask DB
        votes = db.execute("""
            SELECT 
                id,
                match_id,
                player_id,
                created_at
            FROM user_votes
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        
        # Get match and player info from C++ API
        from utils.api_client import _get
        from utils.api_client import API_BASE_URL
        import requests
        
        votes_list = []
        for vote in votes:
            match_id = vote["match_id"]
            player_id = vote["player_id"]
            
            # Get match info from API
            match_info = {"team1": "Команда 1", "team2": "Команда 2", "date": ""}
            try:
                response = requests.get(f"{API_BASE_URL}/matches-page", timeout=3)
                if response.status_code == 200:
                    matches_data = response.json()
                    match = next((m for m in matches_data.get("matches", []) if m.get("id") == match_id), None)
                    if match:
                        match_info = {
                            "team1": match.get("team1", "Команда 1"),
                            "team2": match.get("team2", "Команда 2"),
                            "date": match.get("date", "")
                        }
            except Exception:
                pass
            
            # Get player info from API
            player_info = {"name": "Невідомо", "position": "-"}
            try:
                response = requests.get(f"{API_BASE_URL}/players", timeout=3)
                if response.status_code == 200:
                    players_data = response.json()
                    player = next((p for p in players_data.get("players", []) if p.get("id") == player_id), None)
                    if player:
                        player_info = {
                            "name": player.get("name", "Невідомо"),
                            "position": player.get("position", "-")
                        }
            except Exception:
                pass
            
            votes_list.append({
                "id": vote["id"],
                "match_id": match_id,
                "player_id": player_id,
                "created_at": vote["created_at"],
                "match": match_info,
                "player": player_info
            })
        
        return jsonify({"votes": votes_list})
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting user votes: {e}")
        return jsonify({"error": str(e)}), 500


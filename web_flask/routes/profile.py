"""Profile routes."""
from flask import Blueprint, send_from_directory, request, jsonify, session, g
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
    return send_from_directory(current_app.static_folder, 'profile.html')


@bp.route("/api/profile/votes")
@login_required
def get_user_votes():
    """Get user's voting history."""
    # Allow an optional debug user_id via query param for diagnostics
    user_id = session.get("user_id") or request.args.get("user_id")
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)

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

        # Fetch matches and players from Flask DB (fast, local - not from C++ API)
        matches_map = {}
        players_map = {}
        try:
            # Get matches from Flask cache
            matches = db.execute(
                "SELECT id, team1, team2, date FROM cached_matches").fetchall()
            for m in matches:
                matches_map[m["id"]] = {
                    "team1": m["team1"], "team2": m["team2"], "date": m["date"]}

            # Get players from Flask cache
            players = db.execute(
                "SELECT id, name, position FROM cached_players").fetchall()
            for p in players:
                players_map[p["id"]] = {
                    "name": p["name"], "position": p["position"]}

            # If cache empty, fetch from C++ API and populate cache
            if not matches_map or not players_map:
                import requests
                from utils.api_client import API_BASE_URL

                try:
                    resp = requests.get(
                        f"{API_BASE_URL}/matches-page", timeout=2)
                    if resp.status_code == 200:
                        matches_data = resp.json().get("matches", [])
                        for m in matches_data:
                            mid = m.get("id")
                            matches_map[mid] = {"team1": m.get("team1"), "team2": m.get(
                                "team2"), "date": m.get("date", "")}
                            # Cache it
                            db.execute(
                                "INSERT OR REPLACE INTO cached_matches (id, team1, team2, date) VALUES (?, ?, ?, ?)",
                                (mid, m.get("team1"), m.get(
                                    "team2"), m.get("date", ""))
                            )

                    resp = requests.get(f"{API_BASE_URL}/players", timeout=2)
                    if resp.status_code == 200:
                        players_data = resp.json().get("players", [])
                        for p in players_data:
                            pid = p.get("id")
                            players_map[pid] = {"name": p.get(
                                "name"), "position": p.get("position")}
                            # Cache it
                            db.execute(
                                "INSERT OR REPLACE INTO cached_players (id, name, position, team_id) VALUES (?, ?, ?, ?)",
                                (pid, p.get("name"), p.get(
                                    "position"), p.get("team_id", 0))
                            )
                    db.commit()
                except Exception as api_err:
                    current_app.logger.debug(
                        f"Could not fetch from C++ API: {api_err}")
        except Exception as e:
            current_app.logger.debug(f"Error fetching matches/players: {e}")

        votes_list = []
        for vote in votes:
            match_id = vote["match_id"]
            player_id = vote["player_id"]

            # Lookup match/player info from cached maps; fallback to placeholders
            match = matches_map.get(match_id)
            if match:
                match_info = {
                    "team1": match.get("team1", "Команда 1"),
                    "team2": match.get("team2", "Команда 2"),
                    "date": match.get("date", "")
                }
            else:
                match_info = {"team1": "Команда 1",
                              "team2": "Команда 2", "date": ""}

            player = players_map.get(player_id)
            if player:
                player_info = {"name": player.get(
                    "name", "Невідомо"), "position": player.get("position", "-")}
            else:
                player_info = {"name": "Невідомо", "position": "-"}

            votes_list.append({
                "id": vote["id"],
                "match_id": match_id,
                "player_id": player_id,
                "created_at": vote["created_at"],
                "match": match_info,
                "player": player_info
            })
        # If debug flag provided, include some diagnostics
        debug_mode = request.args.get("debug") == "1"
        result = {"votes": votes_list}
        if debug_mode:
            result["debug"] = {
                "user_id": user_id,
                "votes_count": len(votes_list)
            }
        return jsonify(result)
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting user votes: {e}")
        return jsonify({"error": str(e)}), 500

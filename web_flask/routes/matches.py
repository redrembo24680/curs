"""Matches routes."""
from flask import Blueprint, send_from_directory, request, jsonify, session
import os
import sqlite3
from utils.decorators import login_required
from utils.database import get_db
from utils.api_client import _post

bp = Blueprint('matches', __name__)


@bp.route("/matches")
def matches():
    """Matches page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'matches.html')


@bp.route("/api/vote", methods=["POST"])
@login_required
def vote():
    """Vote for a player - requires authentication. Syncs to both Flask DB and C++ backend."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Потрібно увійти до системи"}), 401

    data = request.get_json()
    match_id = data.get("match_id")
    player_id = data.get("player_id")

    if not match_id or not player_id:
        return jsonify({"status": "error", "message": "match_id та player_id є обов'язковими"}), 400

    # Check if match is active before allowing vote
    from utils.api_client import _get
    try:
        matches_data = _get("/api/match-stats")
        if matches_data and "matches" in matches_data:
            # Find the specific match
            current_match = None
            for match in matches_data["matches"]:
                if match.get("match_id") == int(match_id):
                    current_match = match
                    break
            
            if current_match:
                if not current_match.get("is_active", True):
                    return jsonify({
                        "status": "error", 
                        "message": "Цей матч закрито, голосування недоступне"
                    }), 403
            else:
                return jsonify({"status": "error", "message": "Матч не знайдено"}), 404
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Could not check match status: {e}")
        # Continue anyway if we can't check (backend might be temporarily unavailable)

    # 1. First, send vote to C++ backend (main source of truth)
    try:
        vote_response = _post("/vote", {"match_id": match_id, "player_id": player_id})
        
        if vote_response and vote_response.get("status") == "success":
            # Vote accepted by C++ backend, now save to Flask DB for tracking
            db = get_db()
            try:
                from utils.database import init_user_db
                init_user_db()
                
                db.execute(
                    "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
                    (user_id, match_id, player_id)
                )
                db.commit()
                
                from flask import current_app
                current_app.logger.info(
                    f"Vote synced: user_id={user_id}, match_id={match_id}, player_id={player_id}")
            except sqlite3.IntegrityError:
                # Already voted locally, but C++ backend accepted it
                db.rollback()
            except Exception as e:
                from flask import current_app
                current_app.logger.warning(f"Vote sent to backend but local save failed: {e}")
            
            return jsonify({"status": "success", "message": "Голос зараховано"})
        else:
            # C++ backend rejected the vote
            error_msg = vote_response.get("message", "Помилка при голосуванні") if vote_response else "Помилка з'єднання з сервером"
            return jsonify({"status": "error", "message": error_msg}), 400
            
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error sending vote to backend: {e}")
        
        # Fallback: save locally only if backend is unavailable
        db = get_db()
        try:
            from utils.database import init_user_db
            init_user_db()
            
            db.execute(
                "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
                (user_id, match_id, player_id)
            )
            db.commit()
            return jsonify({
                "status": "success", 
                "message": "Голос збережено локально (backend недоступний)"
            })
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify({
                "status": "error",
                "message": "Ви вже проголосували за цього гравця"
            }), 400
        except Exception as e2:
            from flask import current_app
            current_app.logger.error(f"Error saving vote locally: {e2}")
            return jsonify({
                "status": "error",
                "message": "Помилка збереження голосу"
            }), 500
            # This is not ideal, but we'll continue

    return jsonify({"status": "success", "message": "Голос зараховано"})


@bp.route("/api/vote-status/<int:match_id>")
def vote_status(match_id):
    """Check if current user has voted for any player in this match."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"has_voted": False, "logged_in": False})

    db = get_db()
    try:
        # Get all votes by this user for this match
        votes = db.execute(
            "SELECT player_id FROM user_votes WHERE user_id = ? AND match_id = ?",
            (user_id, match_id)
        ).fetchall()

        if votes:
            # User voted for at least one player in this match
            # Return list of player IDs they voted for
            player_ids = [v["player_id"] for v in votes]
            return jsonify({
                "has_voted": True,
                "logged_in": True,
                "player_ids": player_ids
            })
    except Exception:
        pass

    return jsonify({"has_voted": False, "logged_in": True, "player_ids": []})


@bp.route("/api/user-player-votes")
def user_player_votes():
    """Get list of player IDs that current user has voted for (globally)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"player_ids": []})

    db = get_db()
    try:
        # Get all players this user has voted for (unique by player_id)
        votes = db.execute(
            "SELECT DISTINCT player_id FROM user_votes WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        player_ids = [v["player_id"] for v in votes]
        return jsonify({"player_ids": player_ids})
    except Exception:
        pass

    return jsonify({"player_ids": []})


@bp.route("/api/match-votes/<int:match_id>")
def match_votes(match_id):
    """Get vote counts for all players in a match (from Flask DB, not C++ API)."""
    db = get_db()
    try:
        # Get vote counts for each player in this match from Flask DB
        votes = db.execute(
            """
            SELECT player_id, COUNT(*) as votes
            FROM user_votes
            WHERE match_id = ?
            GROUP BY player_id
            """,
            (match_id,)
        ).fetchall()

        votes_list = [{"player_id": v["player_id"],
                       "votes": v["votes"]} for v in votes]
        return jsonify({"match_id": match_id, "votes": votes_list})
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting match votes: {e}")
        return jsonify({"match_id": match_id, "votes": []}), 500


@bp.route("/api/players-info")
def players_info():
    """Get all players from Flask cache (or C++ API if cache empty)."""
    db = get_db()
    try:
        # Try to get from cache first
        cached = db.execute("SELECT * FROM cached_players").fetchall()
        if cached:
            players = [dict(p) for p in cached]
            return jsonify({"players": players})

        # If cache empty, fetch from C++ API and cache
        import requests
        from utils.api_client import API_BASE_URL

        resp = requests.get(f"{API_BASE_URL}/players", timeout=3)
        if resp.status_code == 200:
            players_data = resp.json().get("players", [])

            # Cache players
            for p in players_data:
                db.execute(
                    """INSERT OR REPLACE INTO cached_players (id, name, position, team_id, votes)
                       VALUES (?, ?, ?, ?, ?)""",
                    (p.get("id"), p.get("name"), p.get("position"),
                     p.get("team_id"), p.get("votes", 0))
                )
            db.commit()

            return jsonify({"players": players_data})
    except Exception as e:
        from flask import current_app
        current_app.logger.debug(f"Error getting players info: {e}")

    return jsonify({"players": []}), 500


@bp.route("/api/matches-info")
def matches_info():
    """Get all matches from Flask cache (or C++ API if cache empty)."""
    db = get_db()
    try:
        # Try to get from cache first
        cached = db.execute("SELECT * FROM cached_matches").fetchall()
        if cached:
            matches = [dict(m) for m in cached]
            return jsonify({"matches": matches})

        # If cache empty, fetch from C++ API and cache
        import requests
        from utils.api_client import API_BASE_URL

        resp = requests.get(f"{API_BASE_URL}/matches-page", timeout=3)
        if resp.status_code == 200:
            matches_data = resp.json().get("matches", [])

            # Cache matches
            for m in matches_data:
                db.execute(
                    """INSERT OR REPLACE INTO cached_matches (id, team1, team2, date, is_active)
                       VALUES (?, ?, ?, ?, ?)""",
                    (m.get("id"), m.get("team1"), m.get("team2"),
                     m.get("date"), m.get("isActive", 1))
                )
            db.commit()

            return jsonify({"matches": matches_data})
    except Exception as e:
        from flask import current_app
        current_app.logger.debug(f"Error getting matches info: {e}")

    return jsonify({"matches": []}), 500


@bp.route("/api/flask-stats")
def flask_stats():
    """Get statistics from C++ backend API."""
    try:
        # Get data directly from C++ backend
        from utils.api_client import _get
        from flask import current_app
        current_app.logger.info("flask_stats: calling _get('/api/stats')")
        stats = _get("/api/stats")
        current_app.logger.info(f"flask_stats: received stats = {stats}")
        
        if stats:
            return jsonify(stats)
        else:
            current_app.logger.warning("flask_stats: stats is empty")
            return jsonify({
                "total_players": 0,
                "total_matches": 0,
                "total_votes": 0,
                "active_matches": 0
            })
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting stats from backend: {e}", exc_info=True)
        return jsonify({
            "total_players": 0,
            "total_matches": 0,
            "total_votes": 0,
            "active_matches": 0
        }), 500

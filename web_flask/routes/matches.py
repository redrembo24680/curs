"""Matches routes."""
from flask import Blueprint, send_file, request, jsonify, session
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
    static_path = os.path.join(current_app.root_path, 'static', 'matches.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/api/vote", methods=["POST"])
@login_required
def vote():
    """Vote for a player - requires authentication. Store vote locally in Flask DB."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Потрібно увійти до системи"}), 401

    data = request.get_json()
    match_id = data.get("match_id")
    player_id = data.get("player_id")

    if not match_id or not player_id:
        return jsonify({"status": "error", "message": "match_id та player_id є обов'язковими"}), 400

    # Save vote in Flask database (local storage)
    db = get_db()
    try:
        # Ensure table exists
        from utils.database import init_user_db
        init_user_db()

        # Try to insert vote
        db.execute(
            "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
            (user_id, match_id, player_id)
        )
        db.commit()

        # Log successful vote for diagnostics
        from flask import current_app
        current_app.logger.info(
            f"Vote recorded: user_id={user_id}, match_id={match_id}, player_id={player_id}")

        return jsonify({"status": "success", "message": "Голос зараховано"})

    except sqlite3.IntegrityError:
        # UNIQUE constraint violation - user already voted for this player
        db.rollback()
        return jsonify({
            "status": "error",
            "message": "Ви вже проголосували за цього гравця",
            "has_voted": True
        }), 400
    except Exception as e:
        db.rollback()
        # Table might not exist, try to create it
        try:
            from utils.database import init_user_db
            init_user_db()
            # Try again after creating table
            db.execute(
                "INSERT INTO user_votes (user_id, match_id, player_id) VALUES (?, ?, ?)",
                (user_id, match_id, player_id)
            )
            db.commit()
            return jsonify({"status": "success", "message": "Голос зараховано"})
        except sqlite3.IntegrityError:
            # Still unique constraint violation
            db.rollback()
            return jsonify({
                "status": "error",
                "message": "Ви вже проголосували за цього гравця"
            }), 400
        except Exception as e2:
            from flask import current_app
            current_app.logger.error(f"Error saving vote to DB: {e2}")
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
    """Get statistics from Flask DB (votes count, etc.)."""
    db = get_db()
    try:
        total_players = db.execute(
            "SELECT COUNT(*) as count FROM cached_players").fetchone()["count"]
        total_matches = db.execute(
            "SELECT COUNT(*) as count FROM cached_matches").fetchone()["count"]
        total_votes = db.execute(
            "SELECT COUNT(*) as count FROM user_votes").fetchone()["count"]

        return jsonify({
            "total_players": total_players,
            "total_matches": total_matches,
            "total_votes": total_votes
        })
    except Exception as e:
        from flask import current_app
        current_app.logger.debug(f"Error getting stats: {e}")
        return jsonify({
            "total_players": 0,
            "total_matches": 0,
            "total_votes": 0
        }), 500

"""Stats routes."""
from flask import Blueprint, send_from_directory, jsonify
import os
from utils.database import get_db

bp = Blueprint('stats', __name__)


@bp.route("/stats")
def stats():
    """Stats page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'stats.html')


@bp.route("/api/stats-page")
def stats_page():
    """Get statistics for stats page - top players and matches with votes from Flask DB."""
    db = get_db()
    try:
        # Get top players by votes from Flask DB
        top_players = db.execute("""
            SELECT 
                p.id,
                p.name,
                p.position,
                COUNT(uv.id) as votes
            FROM cached_players p
            LEFT JOIN user_votes uv ON p.id = uv.player_id
            GROUP BY p.id, p.name, p.position
            ORDER BY votes DESC
            LIMIT 20
        """).fetchall()

        players_list = [{
            "id": p["id"],
            "name": p["name"],
            "position": p["position"],
            "votes": p["votes"]
        } for p in top_players]

        # Get all matches
        matches = db.execute("""
            SELECT 
                id,
                team1,
                team2,
                date,
                team1_goals,
                team2_goals,
                team1_possession,
                team2_possession,
                team1_shots,
                team2_shots,
                team1_shots_on_target,
                team2_shots_on_target,
                team1_corners,
                team2_corners,
                team1_fouls,
                team2_fouls,
                team1_yellow_cards,
                team2_yellow_cards,
                team1_red_cards,
                team2_red_cards
            FROM cached_matches
            ORDER BY date DESC
        """).fetchall()

        matches_list = [{
            "match_id": m["id"],
            "id": m["id"],
            "team1": m["team1"],
            "team2": m["team2"],
            "date": m["date"],
            "team1_goals": m["team1_goals"] or 0,
            "team2_goals": m["team2_goals"] or 0,
            "team1_possession": m["team1_possession"] or 50,
            "team2_possession": m["team2_possession"] or 50,
            "team1_shots": m["team1_shots"] or 0,
            "team2_shots": m["team2_shots"] or 0,
            "team1_shots_on_target": m["team1_shots_on_target"] or 0,
            "team2_shots_on_target": m["team2_shots_on_target"] or 0,
            "team1_corners": m["team1_corners"] or 0,
            "team2_corners": m["team2_corners"] or 0,
            "team1_fouls": m["team1_fouls"] or 0,
            "team2_fouls": m["team2_fouls"] or 0,
            "team1_yellow_cards": m["team1_yellow_cards"] or 0,
            "team2_yellow_cards": m["team2_yellow_cards"] or 0,
            "team1_red_cards": m["team1_red_cards"] or 0,
            "team2_red_cards": m["team2_red_cards"] or 0
        } for m in matches]

        return jsonify({
            "top_players": players_list,
            "matches": matches_list
        })

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting stats page data: {e}")
        return jsonify({
            "top_players": [],
            "matches": []
        }), 500

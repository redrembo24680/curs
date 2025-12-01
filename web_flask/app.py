"""Main Flask application."""
import os
import sqlite3
import time
from flask import Flask, g, session

from config import SECRET_KEY, SESSION_FILE_DIR
from utils.database import close_db, init_user_db, get_db
from utils.teams import sync_teams_and_players
from utils.api_client import get_cached_stats, _get, _post
from routes import (
    auth_bp, dashboard_bp, matches_bp, players_bp, stats_bp, admin_bp, health_bp
)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_FILE_DIR"] = SESSION_FILE_DIR

    # Ensure static files are served with correct headers
    @app.after_request
    def add_static_headers(response):
        """Add headers for static files."""
        if response.content_type and 'text/css' in response.content_type:
            response.headers['Cache-Control'] = 'public, max-age=3600'
        elif response.content_type and 'application/javascript' in response.content_type:
            response.headers['Cache-Control'] = 'public, max-age=3600'
        return response

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)

    # Database teardown
    app.teardown_appcontext(close_db)

    # Bootstrap - initialize database and sync data
    _bootstrap_completed = False

    @app.before_request
    def bootstrap():
        nonlocal _bootstrap_completed
        if not _bootstrap_completed:
            init_user_db()
            try:
                sync_teams_and_players()
                create_sample_matches()
            except Exception as e:
                app.logger.error(f"Bootstrap failed: {e}")
            _bootstrap_completed = True

    @app.before_request
    def load_logged_in_user():
        """Load logged in user from session."""
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
        else:
            try:
                g.user = get_db().execute(
                    "SELECT id, username, role FROM users WHERE id = ?", (user_id,)).fetchone()
            except sqlite3.OperationalError:
                g.user = None

    @app.context_processor
    def inject_globals():
        """Inject global variables into templates."""
        try:
            stats = get_cached_stats()
        except Exception as e:
            app.logger.error(f"Error getting cached stats: {e}")
            stats = {"total_players": 0, "total_matches": 0, "total_votes": 0}
        return {"global_stats": stats, "current_user": g.get("user")}

    def create_sample_matches():
        """Create sample matches if none exist."""
        matches_data = _get(
            "/matches", default={"matches": []}).get("matches", [])
        if matches_data:
            app.logger.info(
                f"Matches already exist ({len(matches_data)}), skipping creation")
            return

        app.logger.info("No matches found, creating sample matches...")
        sample_matches = [
            ("Real Madrid CF", "FC Barcelona"),
            ("Manchester United", "Liverpool FC"),
            ("Bayern Munich", "Borussia Dortmund"),
            ("Paris Saint-Germain", "Olympique de Marseille"),
            ("AC Milan", "Inter Milan"),
        ]

        created = 0
        for team1, team2 in sample_matches:
            ok, result = _post(
                "/matches/add", {"team1": team1, "team2": team2})
            if ok:
                created += 1
                app.logger.info(f"Created sample match: {team1} vs {team2}")
            time.sleep(0.2)  # Small delay

        app.logger.info(f"Created {created} sample matches")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("WEB_PORT", "5000")))

"""Flask application factory - with authentication."""
from flask import Flask, g, session
from config import SECRET_KEY
from utils.database import get_db, close_db, init_user_db
from utils.api_client import get_cached_stats
from utils.logger import setup_logger
from routes import (
    auth_bp, dashboard_bp, matches_bp, players_bp,
    stats_bp, admin_bp, health_bp, profile_bp, comments_bp, posts_bp
)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 hours

    # Setup logging
    setup_logger(app)
    app.logger.info('Flask application starting...')

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
    app.register_blueprint(profile_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(posts_bp)

    # Initialize database on first request
    _bootstrap_completed = False

    @app.before_request
    def bootstrap():
        """Bootstrap database and cache on first request."""
        nonlocal _bootstrap_completed
        if not _bootstrap_completed:
            init_user_db()
            _bootstrap_completed = True

    @app.before_request
    def load_logged_in_user():
        """Load logged in user from session."""
        user_id = session.get("user_id")

        if not user_id:
            g.user = None
            return

        # Try to get from session first
        username = session.get("username")
        role = session.get("role")

        # If we have all session data, create user dict
        if username and role:
            g.user = {
                "id": user_id,
                "username": username,
                "role": role
            }
            return

        # Otherwise, load from database
        try:
            db = get_db()
            user = db.execute(
                "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
            ).fetchone()

            if user:
                # Update session with user data
                session["username"] = user["username"]
                session["role"] = user["role"]
                session.modified = True

                g.user = {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"]
                }
            else:
                # User not found in database, clear session
                session.clear()
                g.user = None
        except Exception as e:
            # Database error, clear session
            app.logger.error(f"Error loading user: {e}")
            session.clear()
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

    @app.teardown_appcontext
    def close_db_handler(error):
        """Close database connection."""
        close_db(error)

    return app

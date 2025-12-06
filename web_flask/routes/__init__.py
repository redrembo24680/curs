"""Route blueprints."""
from .auth import bp as auth_bp
from .dashboard import bp as dashboard_bp
from .matches import bp as matches_bp
from .players import bp as players_bp
from .stats import bp as stats_bp
from .admin import bp as admin_bp
from .health import bp as health_bp
from .profile import bp as profile_bp
from .comments import bp as comments_bp
from .posts import bp as posts_bp

__all__ = ['auth_bp', 'dashboard_bp', 'matches_bp', 'players_bp', 'stats_bp', 'admin_bp', 'health_bp', 'profile_bp', 'comments_bp', 'posts_bp']


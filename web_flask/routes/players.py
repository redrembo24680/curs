"""Players routes."""
from flask import Blueprint, send_file
import os

bp = Blueprint('players', __name__)


@bp.route("/players")
def players():
    """Players page - serve static HTML."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'players.html')
    return send_file(static_path, mimetype='text/html')

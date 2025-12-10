"""Players routes."""
from flask import Blueprint, send_from_directory
import os

bp = Blueprint('players', __name__)


@bp.route("/players")
def players():
    """Players page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'players.html')

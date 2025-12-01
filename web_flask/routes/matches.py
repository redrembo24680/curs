"""Matches routes."""
from flask import Blueprint, send_file
import os

bp = Blueprint('matches', __name__)


@bp.route("/matches")
def matches():
    """Matches page - serve static HTML."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'matches.html')
    return send_file(static_path, mimetype='text/html')


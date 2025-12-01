"""Stats routes."""
from flask import Blueprint, send_file
import os

bp = Blueprint('stats', __name__)


@bp.route("/stats")
def stats():
    """Stats page - serve static HTML."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'stats.html')
    return send_file(static_path, mimetype='text/html')

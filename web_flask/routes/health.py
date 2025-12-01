"""Health check routes."""
from flask import Blueprint, send_file
import os

bp = Blueprint('health', __name__)


@bp.route("/health")
def health():
    """Health check endpoint - serve static HTML."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'health.html')
    return send_file(static_path, mimetype='text/html')

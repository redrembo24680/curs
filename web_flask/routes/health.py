"""Health routes."""
from flask import Blueprint, send_from_directory
import os

bp = Blueprint('health', __name__)


@bp.route("/health")
def health():
    """Health check page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'health.html')

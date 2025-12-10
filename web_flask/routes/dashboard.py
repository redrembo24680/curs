"""Dashboard routes."""
from flask import Blueprint, send_from_directory
import os

bp = Blueprint('dashboard', __name__)


@bp.route("/")
def dashboard():
    """Main dashboard page - serve static HTML."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'index.html')

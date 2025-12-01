"""Dashboard routes."""
from flask import Blueprint, send_from_directory, send_file
import os

bp = Blueprint('dashboard', __name__)


@bp.route("/")
def dashboard():
    """Main dashboard page - serve static HTML."""
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'index.html')
    return send_file(static_path, mimetype='text/html')

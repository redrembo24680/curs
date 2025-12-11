"""Admin routes."""
from flask import Blueprint, jsonify, request, session, redirect, url_for
from functools import wraps
from utils.api_client import _post, _get

bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"error": "Unauthorized"}), 401
        if session.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/api/admin/match/<int:match_id>/close", methods=["POST"])
@admin_required
def close_match(match_id):
    """Close a match (make it inactive)."""
    try:
        success, result = _post("/api/matches/close", {"match_id": str(match_id)})
        if success and result.get("status") == "success":
            return jsonify({"status": "success", "message": "Матч закрито"})
        else:
            error_msg = result.get("message", "Unknown error")
            return jsonify({"status": "error", "message": error_msg}), 500
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error closing match: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/admin/match/<int:match_id>/activate", methods=["POST"])
@admin_required
def activate_match(match_id):
    """Activate a match."""
    try:
        # Use set-active endpoint with is_active=1
        success, result = _post("/api/matches/set-active", {"match_id": str(match_id), "is_active": "1"})
        if success and result.get("status") == "success":
            return jsonify({"status": "success", "message": "Матч активовано"})
        else:
            error_msg = result.get("message", "Unknown error")
            return jsonify({"status": "error", "message": error_msg}), 500
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error activating match: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/admin/match/<int:match_id>/update-stats", methods=["POST"])
@admin_required
def update_match_stats(match_id):
    """Update match statistics."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        # Add match_id to data and convert all to strings
        data["match_id"] = str(match_id)
        # Convert all values to strings for API
        for key in data:
            data[key] = str(data[key])
        
        # Send to C++ backend
        success, result = _post("/api/matches/update-stats", data)
        
        if success and result.get("status") == "success":
            return jsonify({"status": "success", "message": "Статистику оновлено"})
        else:
            error_msg = result.get("message", "Unknown error")
            return jsonify({"status": "error", "message": error_msg}), 500
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error updating match stats: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/api/admin/matches")
@admin_required
def get_all_matches():
    """Get all matches with stats for admin panel."""
    try:
        matches_data = _get("/api/match-stats")
        if matches_data and "matches" in matches_data:
            return jsonify({"matches": matches_data["matches"]})
        else:
            return jsonify({"matches": []}), 500
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting matches: {e}")
        return jsonify({"matches": []}), 500


@bp.route("/admin")
def admin_page():
    """Admin page - serve static HTML."""
    # Check if user is admin
    if not session.get('user_id') or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    from flask import current_app, send_from_directory
    return send_from_directory(current_app.static_folder, 'admin.html')


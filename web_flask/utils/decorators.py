"""Decorators for route protection - completely rewritten."""
from functools import wraps
from flask import jsonify, g, session, request, redirect, url_for


def login_required(view):
    """Decorator to require user login - completely rewritten."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        # Check session first
        user_id = session.get("user_id")
        
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Потрібно увійти до системи"}), 401
            return redirect(url_for("auth.login"))
        
        # Check if g.user is set (from before_request)
        if g.user is None:
            # Try to load from database
            try:
                from utils.database import get_db
                user = get_db().execute(
                    "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
                ).fetchone()
                
                if user:
                    # Set g.user
                    g.user = {
                        "id": user["id"],
                        "username": user["username"],
                        "role": user["role"]
                    }
                    # Update session
                    session["username"] = user["username"]
                    session["role"] = user["role"]
                    session.modified = True
                else:
                    # User not found
                    session.clear()
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({"status": "error", "message": "Користувач не знайдений"}), 401
                    return redirect(url_for("auth.login"))
            except Exception:
                session.clear()
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({"status": "error", "message": "Помилка авторизації"}), 401
                return redirect(url_for("auth.login"))
        
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    """Decorator to require admin role - completely rewritten."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        # First check login
        user_id = session.get("user_id")
        
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Потрібно увійти до системи"}), 401
            return redirect(url_for("auth.login"))
        
        # Get user (from g.user or load from session/db)
        user = None
        if g.user:
            user = g.user
        else:
            # Try session first
            role = session.get("role")
            username = session.get("username")
            if role and username:
                user = {"id": user_id, "username": username, "role": role}
            else:
                # Load from database
                try:
                    from utils.database import get_db
                    db_user = get_db().execute(
                        "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
                    ).fetchone()
                    if db_user:
                        user = {
                            "id": db_user["id"],
                            "username": db_user["username"],
                            "role": db_user["role"]
                        }
                        # Update session
                        session["username"] = db_user["username"]
                        session["role"] = db_user["role"]
                        session.modified = True
                        g.user = user
                except Exception:
                    pass
        
        # Check if user is admin
        if not user or user.get("role") != "admin":
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Дія доступна лише адміністраторам"}), 403
            return redirect(url_for("dashboard.dashboard"))
        
        # Ensure g.user is set
        if not g.user:
            g.user = user
        
        return view(*args, **kwargs)
    return wrapped

"""Authentication routes - completely rewritten."""
from flask import Blueprint, send_file, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote
import os

from utils.database import get_db

bp = Blueprint('auth', __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            return redirect(f"/register?error={quote('Введіть логін та пароль')}")
        
        if len(password) < 6:
            return redirect(f"/register?error={quote('Пароль має містити мінімум 6 символів')}")
        
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, 'fan')",
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(f"/login?success={quote('Реєстрація успішна! Тепер ви можете увійти.')}")
        except Exception:
            db.rollback()
            return redirect(f"/register?error={quote('Користувач з таким логіном вже існує')}")
    
    # GET request - serve static HTML
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'register.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/login", methods=["GET", "POST"])
def login():
    """User login - completely rewritten."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            return redirect(f"/login?error={quote('Введіть логін та пароль')}")
        
        db = get_db()
        user = db.execute(
            "SELECT id, username, password, role FROM users WHERE username = ?", (username,)
        ).fetchone()
        
        if user and check_password_hash(user["password"], password):
            # COMPLETELY CLEAR SESSION FIRST
            session.clear()
            
            # SET ALL SESSION DATA
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session.permanent = True
            session.modified = True
            
            # Force session save
            from flask import current_app
            current_app.logger.info(f"User {username} logged in, session user_id={session.get('user_id')}, role={session.get('role')}")
            
            return redirect(f"/?success={quote(f'Вітаємо, {username}!')}")
        else:
            return redirect(f"/login?error={quote('Невірний логін або пароль')}")
    
    # GET request - serve static HTML
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'login.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/logout")
def logout():
    """User logout."""
    session.clear()
    return redirect(f"/?info={quote('Ви вийшли з системи')}")


@bp.route("/api/user-info")
def user_info():
    """Get current user info - completely rewritten."""
    # First check session
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"logged_in": False})
    
    # Try to get from session first (faster)
    username = session.get("username")
    role = session.get("role")
    
    # If session has all data, return it
    if username and role:
        return jsonify({
            "logged_in": True,
            "username": username,
            "role": role
        })
    
    # Otherwise, load from database
    try:
        db = get_db()
        user = db.execute(
            "SELECT id, username, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        
        if user:
            # Update session with missing data
            if not username:
                session["username"] = user["username"]
            if not role:
                session["role"] = user["role"]
            session.modified = True
            
            return jsonify({
                "logged_in": True,
                "username": user["username"],
                "role": user["role"]
            })
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error loading user info: {e}")
    
    # If user not found, clear session
    session.clear()
    return jsonify({"logged_in": False})

"""Authentication routes."""
from flask import Blueprint, send_file, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
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
            flash("Логін та пароль обов'язкові", "danger")
            return redirect(url_for("auth.register"))
        
        if len(password) < 6:
            flash("Пароль має містити мінімум 6 символів", "danger")
            return redirect(url_for("auth.register"))
        
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, 'fan')",
                (username, generate_password_hash(password))
            )
            db.commit()
            flash("Реєстрація успішна! Тепер ви можете увійти.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.rollback()
            flash("Користувач з таким логіном вже існує", "danger")
            return redirect(url_for("auth.register"))
    
    # GET request - serve static HTML
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'register.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            flash("Введіть логін та пароль", "danger")
            return redirect(url_for("auth.login"))
        
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Вітаємо, {username}!", "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Невірний логін або пароль", "danger")
            return redirect(url_for("auth.login"))
    
    # GET request - serve static HTML
    from flask import current_app
    static_path = os.path.join(current_app.root_path, 'static', 'login.html')
    return send_file(static_path, mimetype='text/html')


@bp.route("/logout")
def logout():
    """User logout - redirect to home."""
    session.clear()
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("dashboard.dashboard"))


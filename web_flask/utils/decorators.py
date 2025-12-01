"""Decorators for route protection."""
from functools import wraps

from flask import flash, g, redirect, request, url_for


def login_required(view):
    """Decorator to require user login."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Потрібно увійти до системи", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    """Decorator to require admin role."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None or g.user["role"] != "admin":
            flash("Дія доступна лише адміністраторам", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return view(*args, **kwargs)
    return wrapped


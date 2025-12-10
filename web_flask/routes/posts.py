"""Posts/News routes."""
from flask import Blueprint, send_from_directory, request, jsonify, session
import os
from utils.decorators import login_required, admin_required
from utils.database import get_db

bp = Blueprint('posts', __name__)


@bp.route("/posts")
def posts():
    """Posts/News page."""
    from flask import current_app
    return send_from_directory(current_app.static_folder, 'posts.html')


@bp.route("/api/posts", methods=["GET"])
def get_posts():
    """Get all posts."""
    db = get_db()
    try:
        posts = db.execute("""
            SELECT 
                p.id,
                p.user_id,
                p.title,
                p.content,
                p.created_at,
                u.username
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """).fetchall()

        posts_list = []
        for post in posts:
            posts_list.append({
                "id": post["id"],
                "user_id": post["user_id"],
                "username": post["username"],
                "title": post["title"],
                "content": post["content"],
                "created_at": post["created_at"],
                "is_own": post["user_id"] == session.get("user_id")
            })

        return jsonify({"posts": posts_list})
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting posts: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/posts", methods=["POST"])
@admin_required
def create_post():
    """Create a new post (admin only)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    db = get_db()
    try:
        cursor = db.execute("""
            INSERT INTO posts (user_id, title, content)
            VALUES (?, ?, ?)
        """, (user_id, title, content))
        db.commit()

        return jsonify({
            "status": "success",
            "message": "Post created",
            "post_id": cursor.lastrowid
        })
    except Exception as e:
        db.rollback()
        from flask import current_app
        current_app.logger.error(f"Error creating post: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/posts/<int:post_id>", methods=["DELETE"])
@admin_required
def delete_post(post_id):
    """Delete a post (admin only)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    db = get_db()
    try:
        # Check if post exists
        post = db.execute(
            "SELECT user_id FROM posts WHERE id = ?", (post_id,)
        ).fetchone()

        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Only allow deleting own posts or if admin
        if post["user_id"] != user_id:
            # Check if user is admin
            user = db.execute(
                "SELECT role FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if not user or user["role"] != "admin":
                return jsonify({"error": "You can only delete your own posts"}), 403

        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()

        return jsonify({"status": "success", "message": "Post deleted"})
    except Exception as e:
        db.rollback()
        from flask import current_app
        current_app.logger.error(f"Error deleting post: {e}")
        return jsonify({"error": str(e)}), 500

"""Comments routes for matches."""
from flask import Blueprint, request, jsonify, session
from utils.decorators import login_required
from utils.database import get_db

bp = Blueprint('comments', __name__)


@bp.route("/api/matches/<int:match_id>/comments", methods=["GET"])
def get_comments(match_id):
    """Get comments for a match."""
    db = get_db()
    try:
        comments = db.execute("""
            SELECT 
                c.id,
                c.user_id,
                c.match_id,
                c.comment_text,
                c.created_at,
                u.username
            FROM match_comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.match_id = ?
            ORDER BY c.created_at DESC
        """, (match_id,)).fetchall()
        
        comments_list = []
        for comment in comments:
            comments_list.append({
                "id": comment["id"],
                "user_id": comment["user_id"],
                "username": comment["username"],
                "comment_text": comment["comment_text"],
                "created_at": comment["created_at"],
                "is_own": comment["user_id"] == session.get("user_id")
            })
        
        return jsonify({"comments": comments_list})
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Error getting comments: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/matches/<int:match_id>/comments", methods=["POST"])
@login_required
def add_comment(match_id):
    """Add a comment to a match."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    comment_text = data.get("comment_text", "").strip()
    
    if not comment_text:
        return jsonify({"error": "Comment text is required"}), 400
    
    db = get_db()
    try:
        db.execute("""
            INSERT INTO match_comments (user_id, match_id, comment_text)
            VALUES (?, ?, ?)
        """, (user_id, match_id, comment_text))
        db.commit()
        
        return jsonify({"status": "success", "message": "Comment added"})
    except Exception as e:
        db.rollback()
        from flask import current_app
        current_app.logger.error(f"Error adding comment: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    """Delete a comment (only own comments)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    db = get_db()
    try:
        # Check if comment belongs to user
        comment = db.execute(
            "SELECT user_id FROM match_comments WHERE id = ?", (comment_id,)
        ).fetchone()
        
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        
        if comment["user_id"] != user_id:
            return jsonify({"error": "You can only delete your own comments"}), 403
        
        db.execute("DELETE FROM match_comments WHERE id = ?", (comment_id,))
        db.commit()
        
        return jsonify({"status": "success", "message": "Comment deleted"})
    except Exception as e:
        db.rollback()
        from flask import current_app
        current_app.logger.error(f"Error deleting comment: {e}")
        return jsonify({"error": str(e)}), 500



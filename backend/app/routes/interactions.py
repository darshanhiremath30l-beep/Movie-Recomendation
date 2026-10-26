from flask import Blueprint, jsonify, request
from ..services.recommendation_service import compute_recommendations_for_user
from ..db import get_db, get_users_collection
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

interactions_bp = Blueprint('interactions', __name__)

def record_interaction(user_id, movie_id, action_type, metadata=None):
    db = get_db()
    if db is None:
        return
        
    interaction = {
        "user_id": str(user_id),
        "movie_id": movie_id,
        "action_type": action_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }
    db.interactions.insert_one(interaction)

def _update_user_field(users, user_id, update_dict):
    if not users or user_id == "default_user":
        return
    # Try ObjectId first
    try:
        res = users.update_one({"_id": ObjectId(user_id)}, update_dict)
        if hasattr(res, 'matched_count') and res.matched_count > 0:
            return
    except (InvalidId, Exception):
        pass
    # Fallback to string ID
    try:
        users.update_one({"_id": str(user_id)}, update_dict)
    except Exception:
        pass

@interactions_bp.route('/like', methods=['POST'])
def like_movie():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    movie_id = data.get("movie_id")
    
    if movie_id:
        try:
            record_interaction(user_id, movie_id, "like")
            users = get_users_collection()
            _update_user_field(users, user_id, {"$addToSet": {"likes": movie_id}})
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    return jsonify({"message": "Liked successfully", "recommendations": recs}), 200

@interactions_bp.route('/rate', methods=['POST'])
def rate_movie():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    
    if movie_id and rating:
        try:
            record_interaction(user_id, movie_id, "rate", {"rating": rating})
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    return jsonify({"message": "Rated successfully", "recommendations": recs}), 200

@interactions_bp.route('/watch', methods=['POST'])
def watch_movie():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    movie_id = data.get("movie_id")
    
    if movie_id:
        try:
            record_interaction(user_id, movie_id, "watch")
            users = get_users_collection()
            _update_user_field(users, user_id, {"$addToSet": {"watch_history": movie_id}})
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    return jsonify({"message": "Added to watch history and updated recommendations", "recommendations": recs}), 200

@interactions_bp.route('/watchlist', methods=['POST', 'DELETE'])
def watchlist():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    movie_id = data.get("movie_id")
    action = "add_watchlist" if request.method == 'POST' else "remove_watchlist"
    
    if movie_id:
        try:
            record_interaction(user_id, movie_id, action)
            users = get_users_collection()
            update_op = "$addToSet" if request.method == 'POST' else "$pull"
            _update_user_field(users, user_id, {update_op: {"watchlist": movie_id}})
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    msg = "Added to watchlist" if request.method == 'POST' else "Removed from watchlist"
    return jsonify({"message": msg, "recommendations": recs}), 200

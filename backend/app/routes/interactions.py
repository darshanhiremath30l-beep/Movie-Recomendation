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
        "user_id": user_id,
        "movie_id": movie_id,
        "action_type": action_type,
        "timestamp": datetime.now(timezone.utc),
        "metadata": metadata or {}
    }
    db.interactions.insert_one(interaction)

@interactions_bp.route('/like', methods=['POST'])
def like_movie():
    data = request.json or {}
    user_id = data.get("user_id", "default_user")
    movie_id = data.get("movie_id")
    
    if movie_id:
        try:
            record_interaction(user_id, movie_id, "like")
            users = get_users_collection()
            if users is not None and user_id != "default_user":
                try:
                    users.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"likes": movie_id}})
                except InvalidId:
                    pass
        except Exception:
            pass # Ignore if DB not running
            
    # Trigger refresh
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
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    return jsonify({"message": "Added to watch history", "recommendations": recs}), 200

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
            if users is not None and user_id != "default_user":
                try:
                    update_action = "$addToSet" if request.method == 'POST' else "$pull"
                    users.update_one({"_id": ObjectId(user_id)}, {update_action: {"watchlist": movie_id}})
                except InvalidId:
                    pass
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    msg = "Added to watchlist" if request.method == 'POST' else "Removed from watchlist"
    return jsonify({"message": msg, "recommendations": recs}), 200

from flask import Blueprint, jsonify, request
from ..services.recommendation_service import compute_recommendations_for_user
from ..services.omdb_service import get_movie_details
from ..db import (
    get_db, 
    get_users_collection, 
    get_watchlist_collection, 
    get_liked_movies_collection, 
    get_recently_watched_collection
)
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
    try:
        db.interactions.insert_one(interaction)
    except Exception:
        pass

def _get_movie_info(movie_id):
    """Helper to get movie title & poster for table records."""
    db = get_db()
    title = ""
    poster = ""
    duration = ""
    try:
        if db is not None:
            m = db.movies.find_one({"movie_id": movie_id}) or db.movies.find_one({"id": movie_id})
            if m:
                title = m.get("title", "")
                poster = m.get("poster", "")
                duration = m.get("duration", "")
    except Exception:
        pass
        
    if not title:
        try:
            details = get_movie_details(movie_id)
            if details:
                title = details.get("title", "")
                poster = details.get("poster", "")
                duration = details.get("duration", "")
        except Exception:
            pass
            
    return {"title": title, "poster": poster, "duration": duration}

def _update_user_field(users, user_id, update_dict):
    if users is None or user_id == "default_user":
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
    except Exception as e:
        print(f"Notice _update_user_field: {e}")

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
            
            # Sync to dedicated 'liked_movies' collection
            liked_coll = get_liked_movies_collection()
            if liked_coll is not None:
                movie_info = _get_movie_info(movie_id)
                liked_coll.update_one(
                    {"user_id": str(user_id), "movie_id": movie_id},
                    {"$set": {
                        "user_id": str(user_id),
                        "movie_id": movie_id,
                        "title": movie_info["title"],
                        "poster": movie_info["poster"],
                        "liked_at": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
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
            db = get_db()
            if db is not None:
                movie_info = _get_movie_info(movie_id)
                db.ratings.update_one(
                    {"user_id": str(user_id), "movie_id": movie_id},
                    {"$set": {
                        "user_id": str(user_id),
                        "movie_id": movie_id,
                        "rating": float(rating),
                        "title": movie_info["title"],
                        "rated_at": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
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
            
            # Sync to dedicated 'recently_watched' collection
            rw_coll = get_recently_watched_collection()
            if rw_coll is not None:
                movie_info = _get_movie_info(movie_id)
                rw_coll.update_one(
                    {"user_id": str(user_id), "movie_id": movie_id},
                    {"$set": {
                        "user_id": str(user_id),
                        "movie_id": movie_id,
                        "title": movie_info["title"],
                        "duration": movie_info["duration"],
                        "poster": movie_info["poster"],
                        "watched_at": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
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
            
            # Sync to dedicated 'watchlist' collection
            wl_coll = get_watchlist_collection()
            if wl_coll is not None:
                if request.method == 'POST':
                    movie_info = _get_movie_info(movie_id)
                    wl_coll.update_one(
                        {"user_id": str(user_id), "movie_id": movie_id},
                        {"$set": {
                            "user_id": str(user_id),
                            "movie_id": movie_id,
                            "title": movie_info["title"],
                            "poster": movie_info["poster"],
                            "added_at": datetime.now(timezone.utc).isoformat()
                        }},
                        upsert=True
                    )
                else:
                    wl_coll.delete_one({"user_id": str(user_id), "movie_id": movie_id})
        except Exception:
            pass
            
    recs = compute_recommendations_for_user(user_id)
    msg = "Added to watchlist" if request.method == 'POST' else "Removed from watchlist"
    return jsonify({"message": msg, "recommendations": recs}), 200

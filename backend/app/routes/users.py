from flask import Blueprint, jsonify, request
from ..db import (
    get_users_collection, 
    get_watchlist_collection, 
    get_liked_movies_collection, 
    get_recently_watched_collection, 
    serialize_doc
)
from ..local_db import local_db
from ..services.omdb_service import get_movie_details
from bson import ObjectId
from bson.errors import InvalidId

users_bp = Blueprint('users', __name__)

@users_bp.route('/<user_id>/watchlist', methods=['GET'])
def get_watchlist(user_id):
    try:
        # Check dedicated watchlist collection first
        wl_coll = get_watchlist_collection()
        if wl_coll is not None:
            items = list(wl_coll.find({"user_id": str(user_id)}, {"_id": 0}))
            if items:
                # If records have full movie details, return them directly
                return jsonify({"data": serialize_doc(items)}), 200

        # Fallback: check user's watchlist array
        users = get_users_collection() or local_db['users']
        user = None
        try:
            user = users.find_one({"_id": ObjectId(user_id)})
        except (InvalidId, Exception):
            pass
            
        if not user:
            user = users.find_one({"_id": str(user_id)})
            
        if not user:
            return jsonify({"message": "User not found or empty watchlist", "data": []}), 200
            
        watchlist_ids = user.get("watchlist", [])
        populated_movies = []
        for movie_id in watchlist_ids:
            details = get_movie_details(movie_id)
            if details:
                populated_movies.append(details)
                
        return jsonify({"data": populated_movies}), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "data": []}), 500

@users_bp.route('/<user_id>/recently-watched', methods=['GET'])
def get_recently_watched(user_id):
    try:
        rw_coll = get_recently_watched_collection()
        if rw_coll is not None:
            items = list(rw_coll.find({"user_id": str(user_id)}).sort("watched_at", -1))
            return jsonify({"data": serialize_doc(items)}), 200
        return jsonify({"data": []}), 200
    except Exception as e:
        return jsonify({"error": str(e), "data": []}), 500

@users_bp.route('/<user_id>/liked', methods=['GET'])
def get_liked_movies(user_id):
    try:
        liked_coll = get_liked_movies_collection()
        if liked_coll is not None:
            items = list(liked_coll.find({"user_id": str(user_id)}).sort("liked_at", -1))
            return jsonify({"data": serialize_doc(items)}), 200
        return jsonify({"data": []}), 200
    except Exception as e:
        return jsonify({"error": str(e), "data": []}), 500

@users_bp.route('/profile', methods=['GET'])
def get_profile():
    return jsonify({"message": "User profile data here."}), 200

@users_bp.route('/preferences', methods=['POST', 'GET'])
def user_preferences():
    return jsonify({"message": "Preferences updated successfully."}), 200

@users_bp.route('/history', methods=['POST', 'GET'])
def watch_history():
    return jsonify({"message": "User watch history."}), 200

@users_bp.route('/ratings', methods=['POST'])
def submit_rating():
    return jsonify({"message": "Rating submitted successfully."}), 200

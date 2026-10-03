from flask import Blueprint, jsonify, request
from ..db import get_users_collection, serialize_doc
from ..services.omdb_service import get_movie_details
from bson import ObjectId
from bson.errors import InvalidId

users_bp = Blueprint('users', __name__)

@users_bp.route('/<user_id>/watchlist', methods=['GET'])
def get_watchlist(user_id):
    try:
        users = get_users_collection()
        if users is None:
            return jsonify({"error": "Database unavailable", "data": []}), 503
            
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found", "data": []}), 404
            
        watchlist_ids = user.get("watchlist", [])
        
        populated_movies = []
        for movie_id in watchlist_ids:
            # Resolves OMDB movie via DB cache, fast
            details = get_movie_details(movie_id)
            if details:
                populated_movies.append(details)
                
        return jsonify({"data": populated_movies}), 200
        
    except InvalidId:
        return jsonify({"error": "Invalid user ID form", "data": []}), 400
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

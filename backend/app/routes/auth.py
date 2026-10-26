from flask import Blueprint, jsonify, request
from ..db import get_users_collection, serialize_doc
from ..local_db import local_db
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

def _get_users():
    users = get_users_collection()
    if users is None:
        return local_db['users']
    return users

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with email verification."""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        users = _get_users()
        user = users.find_one({"email": email})
        
        if not user:
            return jsonify({
                "error": "User not found. Please click 'Sign Up' to create your account, or use demo@example.com / password123"
            }), 404
        
        # Verify password (with fallback for legacy plaintext accounts)
        stored_password = user.get("password", "")
        if stored_password:
            valid = False
            try:
                valid = check_password_hash(stored_password, password)
            except Exception:
                pass
            if not valid and stored_password != password:
                return jsonify({"error": "Invalid password"}), 401
                
        return jsonify({
            "message": "Login successful",
            "user": serialize_doc(user),
            "token": "jwt-token-placeholder"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration - creates new user in MongoDB or local database."""
    data = request.json or {}
    email = data.get('email', '').strip()
    name = data.get('name', '').strip()
    password = data.get('password', '')
    
    if not email or not name:
        return jsonify({"error": "Email and name are required"}), 400
    
    try:
        users = _get_users()
        
        # Check if user already exists
        existing_user = users.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "User already exists with this email"}), 409
        
        # Create new user document
        new_user = {
            "_id": str(ObjectId()),
            "name": name,
            "email": email,
            "password": generate_password_hash(password) if password else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "watchlist": [],
            "likes": [],
            "ratings": [],
            "watch_history": []
        }
        
        result = users.insert_one(new_user)
        if hasattr(result, 'inserted_id') and result.inserted_id:
            new_user['_id'] = str(result.inserted_id)
        
        return jsonify({
            "message": "User created successfully",
            "user": serialize_doc(new_user),
            "token": "jwt-token-placeholder"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Alias for register endpoint - creates user in MongoDB or local database."""
    data = request.json or {}
    email = data.get('email', '').strip()
    name = data.get('name', 'Movie Fan').strip()
    password = data.get('password', '')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        users = _get_users()
        
        # Check if user already exists
        existing = users.find_one({"email": email})
        if existing:
            return jsonify({"error": "User already exists with this email"}), 409
        
        user_doc = {
            "_id": str(ObjectId()),
            "name": name,
            "email": email,
            "password": generate_password_hash(password) if password else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "watchlist": [],
            "likes": [],
            "ratings": [],
            "watch_history": []
        }
        
        result = users.insert_one(user_doc)
        if hasattr(result, 'inserted_id') and result.inserted_id:
            user_doc['_id'] = str(result.inserted_id)
        
        return jsonify({
            "message": "User created",
            "user": serialize_doc(user_doc),
            "token": "jwt-token-placeholder"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

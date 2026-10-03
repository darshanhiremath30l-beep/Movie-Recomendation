from flask import Blueprint, jsonify, request
from app.db import get_users_collection, serialize_doc
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with email verification."""
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        users = get_users_collection()
        if users is None:
            return jsonify({"error": "Database unavailable - running in offline mode"}), 503
        
        user = users.find_one({"email": email})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify password (with fallback for legacy plaintext accounts)
        stored_password = user.get("password", "")
        if not stored_password or not check_password_hash(stored_password, password):
            if stored_password != password:
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
    """User registration - creates new user in MongoDB."""
    data = request.json or {}
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if not email or not name:
        return jsonify({"error": "Email and name are required"}), 400
    
    try:
        users = get_users_collection()
        if users is None:
            return jsonify({"error": "Database unavailable - running in offline mode"}), 503
        
        # Check if user already exists
        existing_user = users.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        
        # Create new user document
        new_user = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password) if password else "",
            "created_at": ObjectId(),
            "watchlist": [],
            "ratings": []
        }
        
        result = users.insert_one(new_user)
        new_user['_id'] = result.inserted_id
        
        return jsonify({
            "message": "User created successfully",
            "user": serialize_doc(new_user)
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Alias for register endpoint - creates user in MongoDB."""
    data = request.json or {}
    email = data.get('email')
    name = data.get('name', 'Keertana')  # Default name if not provided
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    try:
        users = get_users_collection()
        if users is None:
            return jsonify({"error": "Database unavailable - running in offline mode"}), 503
        
        # Check if user already exists
        existing = users.find_one({"email": email})
        if existing:
            return jsonify({"error": "User already exists"}), 409
        
        user_doc = {
            "name": name,
            "email": email,
            "created_at": ObjectId(),
            "watchlist": [],
            "ratings": []
        }
        
        result = users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        
        return jsonify({
            "message": "User created",
            "user": serialize_doc(user_doc)
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

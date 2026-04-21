from flask import Blueprint, jsonify, request
from ..services.recommendation_service import compute_recommendations_for_user

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/for-you', methods=['GET'])
def get_recommendations():
    user_id = request.args.get("user_id", "default_user")
    recs = compute_recommendations_for_user(user_id)
    return jsonify({
        "message": "AI Recommendations computed successfully",
        "data": recs
    }), 200

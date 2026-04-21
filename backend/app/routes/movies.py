from flask import Blueprint, jsonify, request
from ..services.omdb_service import search_movies, get_movie_details, get_trailer_url

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/search', methods=['GET'])
def search_for_movies():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"data": []}), 200
        
    results = search_movies(query)
    return jsonify({"data": results}), 200

@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    details = get_movie_details(movie_id)
    if details:
        return jsonify({"data": details}), 200
    return jsonify({"error": "Movie not found"}), 404

@movies_bp.route('/<movie_id>/trailer', methods=['GET'])
def get_trailer(movie_id):
    # We first need the title to search youtube
    details = get_movie_details(movie_id)
    if details and "title" in details:
        link = get_trailer_url(f"{details['title']} {details.get('year', '')}")
        if link:
            return jsonify({"trailer_url": link}), 200
    return jsonify({"error": "Trailer not found"}), 404

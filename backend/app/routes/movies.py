import re
from flask import Blueprint, jsonify, request
from ..services.omdb_service import search_movies as search_omdb, get_movie_details, get_trailer_url
from ..services.tmdb_service import get_indian_movies, search_tmdb_movies
from ..services.watchmode_service import get_live_releases, search_watchmode_movies, get_streaming_sources
from ..db import get_collection

movies_bp = Blueprint('movies', __name__)

LANGUAGE_KEYWORDS = {
    'kannada': 'Kannada',
    'kannada movie': 'Kannada',
    'kannada movies': 'Kannada',
    'sandalwood': 'Kannada',
    'telugu': 'Telugu',
    'telugu movie': 'Telugu',
    'telugu movies': 'Telugu',
    'tollywood': 'Telugu',
    'hindi': 'Hindi',
    'hindi movie': 'Hindi',
    'hindi movies': 'Hindi',
    'bollywood': 'Hindi',
    'tamil': 'Tamil',
    'tamil movie': 'Tamil',
    'tamil movies': 'Tamil',
    'kollywood': 'Tamil',
    'malayalam': 'Malayalam',
    'malayalam movie': 'Malayalam',
    'malayalam movies': 'Malayalam',
    'mollywood': 'Malayalam',
}

@movies_bp.route('/indian', methods=['GET'])
def fetch_indian_movies():
    """Endpoint to fetch live trending Indian movies across languages."""
    lang = request.args.get('lang', 'all').lower()
    page = request.args.get('page', 1, type=int)
    results = get_indian_movies(language=lang, page=page)
    return jsonify({"data": results, "language": lang, "count": len(results)}), 200

@movies_bp.route('/live', methods=['GET'])
def fetch_live_movies():
    """Endpoint to fetch real-time live streaming releases via Watchmode."""
    limit = request.args.get('limit', 16, type=int)
    releases = get_live_releases(limit=limit)
    return jsonify({"data": releases, "count": len(releases)}), 200

@movies_bp.route('/search', methods=['GET'])
def search_for_movies():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"data": []}), 200

    q_lower = query.lower()
    # Strip common search suffix filler words (movies, movie, film, films)
    clean_keyword = re.sub(r'\b(movies?|films?|cinema)\b', '', q_lower).strip()

    combined_results = []
    seen_titles = set()

    def add_result(movie):
        if not movie:
            return
        title_key = movie.get('title', '').strip().lower()
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            combined_results.append(movie)

    # 1. Detect if this is a language query (e.g. "kannada movies", "telugu", "hindi")
    matched_language = None
    for k, lang in LANGUAGE_KEYWORDS.items():
        if k in q_lower:
            matched_language = lang
            break

    # 2. Search local database / MongoDB collections
    movies_coll = get_collection('movies')
    if movies_coll is not None:
        try:
            db_query = {}
            if matched_language:
                db_query = {
                    "$or": [
                        {"genres": {"$regex": f"^{matched_language}$", "$options": "i"}},
                        {"title": {"$regex": matched_language, "$options": "i"}},
                        {"synopsis": {"$regex": matched_language, "$options": "i"}}
                    ]
                }
            elif clean_keyword:
                regex_pattern = {"$regex": re.escape(clean_keyword), "$options": "i"}
                db_query = {
                    "$or": [
                        {"title": regex_pattern},
                        {"genres": regex_pattern},
                        {"cast": regex_pattern},
                        {"director": regex_pattern},
                        {"synopsis": regex_pattern}
                    ]
                }
            
            if db_query:
                cursor = movies_coll.find(db_query, {"_id": 0})
                for doc in cursor:
                    doc["id"] = doc.get("movie_id") or doc.get("id")
                    add_result(doc)
        except Exception as e:
            print(f"Notice: DB search error: {e}")

    # 3. If language detected, optionally enrich from TMDB if catalog has fewer results
    if matched_language:
        if len(combined_results) < 5:
            try:
                tmdb_lang_code = matched_language.lower()
                tmdb_results = get_indian_movies(language=tmdb_lang_code, page=1)
                for m in tmdb_results:
                    add_result(m)
            except Exception:
                pass
    else:
        # 4. Search external TMDB & OMDB with the clean search term
        search_term = clean_keyword if clean_keyword else query
        try:
            tmdb_matches = search_tmdb_movies(search_term)
            for m in tmdb_matches:
                add_result(m)
        except Exception:
            pass

        if len(combined_results) < 5:
            try:
                omdb_matches = search_omdb(search_term)
                for m in omdb_matches:
                    add_result(m)
            except Exception:
                pass

        if len(combined_results) < 5:
            try:
                wm_matches = search_watchmode_movies(search_term)
                for m in wm_matches:
                    add_result(m)
            except Exception:
                pass

    return jsonify({"data": combined_results, "count": len(combined_results)}), 200

@movies_bp.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    # Check database first
    movies_coll = get_collection('movies')
    if movies_coll is not None:
        try:
            local_movie = movies_coll.find_one({"movie_id": movie_id}, {"_id": 0})
            if local_movie:
                local_movie["id"] = local_movie["movie_id"]
                return jsonify({"data": local_movie}), 200
        except Exception:
            pass

    details = get_movie_details(movie_id)
    if details:
        return jsonify({"data": details}), 200
    return jsonify({"error": "Movie not found"}), 404

@movies_bp.route('/<movie_id>/trailer', methods=['GET'])
def get_trailer(movie_id):
    # Check database title first
    movies_coll = get_collection('movies')
    title = None
    year = ''
    if movies_coll is not None:
        try:
            local_movie = movies_coll.find_one({"movie_id": movie_id})
            if local_movie:
                title = local_movie.get('title')
                year = local_movie.get('year', '')
        except Exception:
            pass

    if not title:
        details = get_movie_details(movie_id)
        if details and "title" in details:
            title = details['title']
            year = details.get('year', '')

    if title:
        link = get_trailer_url(f"{title} {year}")
        if link:
            return jsonify({"trailer_url": link}), 200

    return jsonify({"error": "Trailer not found"}), 404

@movies_bp.route('/<movie_id>/sources', methods=['GET'])
def get_sources(movie_id):
    """Endpoint to fetch live streaming options (Netflix, Prime, JioCinema, Hotstar, etc.) for a movie."""
    region = request.args.get('region', 'IN').upper()
    sources = get_streaming_sources(movie_id, preferred_region=region)
    return jsonify({"data": sources, "movie_id": movie_id, "region": region, "count": len(sources)}), 200

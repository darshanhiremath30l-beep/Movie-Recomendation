import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bson import ObjectId
from bson.errors import InvalidId
from ..db import (
    get_db,
    get_users_collection,
    get_liked_movies_collection,
    get_watchlist_collection,
    get_recently_watched_collection,
    get_ratings_collection
)

FALLBACK_MOVIES = [
    {
        "id": "tt12735488",
        "title": "Kalki 2898 AD",
        "genres": ["Telugu", "Action", "Sci-Fi"],
        "rating": 7.6,
        "year": 2024,
        "duration": "3h 0m",
        "synopsis": "When the world is consumed by darkness, a modern avatar descends to earth to protect the innocent from evil forces in a futuristic post-apocalyptic world.",
        "poster": "https://m.media-amazon.com/images/M/MV5BZjJhMTFiN2UtMmQ4MC00MTZjLTk3NDYtYWRkNTFmNDQwNDFjXkEyXkFqcGc@._V1_SX300.jpg",
        "match_score": "95% Match",
        "ai_reason": "Trending Epic Sci-Fi"
    },
    {
        "id": "tt15239678",
        "title": "Dune: Part Two",
        "genres": ["Sci-Fi", "Adventure", "Action"],
        "rating": 8.5,
        "year": 2024,
        "duration": "2h 46m",
        "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
        "match_score": "94% Match",
        "ai_reason": "Critically Acclaimed Sci-Fi"
    },
    {
        "id": "tt6263850",
        "title": "Deadpool & Wolverine",
        "genres": ["Action", "Comedy", "Sci-Fi"],
        "rating": 7.7,
        "year": 2024,
        "duration": "2h 8m",
        "synopsis": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool to defeat a common enemy.",
        "poster": "https://m.media-amazon.com/images/M/MV5BNzRiMjg0MzUtNTNhYi00N2Q5LWEwMzMtYWJiM2M1M2VkOGU1XkEyXkFqcGc@._V1_SX300.jpg",
        "match_score": "91% Match",
        "ai_reason": "High-Energy Action Comedy"
    }
]

def fetch_movies():
    """Fetch movie catalog from MongoDB Atlas or fallback."""
    try:
        db = get_db()
        if db is not None:
            movies = list(db.movies.find({}, {"_id": 0}))
            if movies:
                return pd.DataFrame(movies)
    except Exception as e:
        print(f"Notice: fetch_movies fallback: {e}")
    return pd.DataFrame(FALLBACK_MOVIES)

def build_movie_features(row):
    """
    Construct weighted multi-modal text representation:
    - Genres (weighted 3x)
    - Director (weighted 2x)
    - Cast (weighted 2x)
    - Synopsis keywords (weighted 1x)
    """
    genres = row.get('genres', [])
    if isinstance(genres, list):
        genres_str = ' '.join(genres)
    else:
        genres_str = str(genres) if pd.notna(genres) else ''
        
    cast = row.get('cast', [])
    if isinstance(cast, list):
        cast_str = ' '.join([c.replace(' ', '_') for c in cast])
    else:
        cast_str = str(cast) if pd.notna(cast) else ''
        
    director = str(row.get('director', '')).replace(' ', '_') if pd.notna(row.get('director')) else ''
    synopsis = str(row.get('synopsis', '')) if pd.notna(row.get('synopsis')) else ''
    
    # Repeat key signals to boost their importance in TF-IDF cosine vector space
    features = f"{genres_str} {genres_str} {genres_str} {director} {director} {cast_str} {cast_str} {synopsis}"
    return features.strip().lower()

def gather_user_profile(user_id):
    """
    Gathers user affinity signals across all MongoDB tables:
    - liked_movies (weight: 3.0)
    - watchlist (weight: 2.0)
    - recently_watched (weight: 1.8)
    - ratings (weight: -1.5 to +2.5 based on score)
    - users document (fallback/synced arrays)
    """
    weights = {}  # movie_id -> float weight
    source_reasons = {}  # movie_id -> (reason_label, movie_title)
    user_email = None

    db = get_db()
    if db is None:
        return weights, source_reasons

    # 1. Look up user document
    users_coll = get_users_collection()
    user_doc = None
    if users_coll is not None and user_id and user_id != "default_user":
        try:
            user_doc = users_coll.find_one({"_id": ObjectId(user_id)})
        except (InvalidId, Exception):
            pass
        if not user_doc:
            user_doc = users_coll.find_one({"_id": str(user_id)})
        if not user_doc and "@" in str(user_id):
            user_doc = users_coll.find_one({"email": str(user_id)})
            
        if user_doc:
            user_email = user_doc.get("email")

    user_query = {"$or": [{"user_id": str(user_id)}]}
    if user_email:
        user_query["$or"].append({"user_email": user_email})
        user_query["$or"].append({"user_id": user_email})

    # If default_user, check if we have any interactions or demo user data
    if user_id == "default_user" or not user_doc:
        # Check if demo user exists in users table
        demo = users_coll.find_one({"email": "demo@example.com"}) if users_coll is not None else None
        if demo:
            user_query["$or"].extend([
                {"user_id": str(demo.get("_id"))},
                {"user_email": "demo@example.com"},
                {"user_id": "demo@example.com"}
            ])

    # 2. Liked Movies (Strongest explicit preference)
    try:
        liked_coll = get_liked_movies_collection()
        if liked_coll is not None:
            for item in liked_coll.find(user_query):
                mid = item.get("movie_id")
                if mid:
                    weights[mid] = weights.get(mid, 0.0) + 3.0
                    source_reasons[mid] = ("liked", item.get("title", ""))
    except Exception as e:
        print(f"Notice: liked_movies query: {e}")

    # 3. Watchlist (High interest intent)
    try:
        wl_coll = get_watchlist_collection()
        if wl_coll is not None:
            for item in wl_coll.find(user_query):
                mid = item.get("movie_id")
                if mid:
                    weights[mid] = weights.get(mid, 0.0) + 2.0
                    if mid not in source_reasons:
                        source_reasons[mid] = ("watchlist", item.get("title", ""))
    except Exception as e:
        print(f"Notice: watchlist query: {e}")

    # 4. Recently Watched (Active engagement)
    try:
        rw_coll = get_recently_watched_collection()
        if rw_coll is not None:
            # Newest watched first
            for item in rw_coll.find(user_query).sort("watched_at", -1):
                mid = item.get("movie_id")
                if mid:
                    weights[mid] = weights.get(mid, 0.0) + 1.8
                    if mid not in source_reasons:
                        source_reasons[mid] = ("watched", item.get("title", ""))
    except Exception as e:
        print(f"Notice: recently_watched query: {e}")

    # 5. Ratings table
    try:
        ratings_coll = get_ratings_collection()
        if ratings_coll is not None:
            for item in ratings_coll.find(user_query):
                mid = item.get("movie_id")
                r_val = float(item.get("rating", 0))
                if mid and r_val > 0:
                    if r_val >= 8.0:
                        weights[mid] = weights.get(mid, 0.0) + 2.5
                    elif r_val >= 6.0:
                        weights[mid] = weights.get(mid, 0.0) + 1.2
                    elif r_val <= 4.0:
                        weights[mid] = weights.get(mid, 0.0) - 1.5
    except Exception as e:
        print(f"Notice: ratings query: {e}")

    # 6. Fallback from user_doc arrays
    if user_doc:
        for mid in user_doc.get("likes", []):
            if mid not in weights:
                weights[mid] = weights.get(mid, 0.0) + 3.0
                source_reasons[mid] = ("liked", "")
        for mid in user_doc.get("watchlist", []):
            if mid not in weights:
                weights[mid] = weights.get(mid, 0.0) + 2.0
                source_reasons[mid] = ("watchlist", "")
        for mid in user_doc.get("watch_history", []):
            if mid not in weights:
                weights[mid] = weights.get(mid, 0.0) + 1.8
                source_reasons[mid] = ("watched", "")

    return weights, source_reasons

def compute_recommendations_for_user(user_id="default_user", limit=6):
    """
    Computes personalized AI recommendations for a specific user using:
    - Multi-table MongoDB signals (liked_movies, watchlist, recently_watched, ratings, users)
    - TF-IDF Vectorization over genres, cast, director, and synopsis
    - Weighted Cosine Similarity Profile Vector
    - Explainable AI (XAI) output reasons ('Because you liked X', match percentages)
    """
    df = fetch_movies()
    if df.empty:
        return FALLBACK_MOVIES

    # Standardize movie IDs
    movie_id_col = 'movie_id' if 'movie_id' in df.columns else 'id'
    df['id'] = df[movie_id_col].astype(str)

    # Build rich features
    df['features'] = df.apply(build_movie_features, axis=1)

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(df['features'])

    # Gather weights and sources from MongoDB
    user_weights, source_reasons = gather_user_profile(user_id)

    # Find which movies in our catalog match user's interactions
    interacted_indices = []
    interacted_weights = []
    interacted_ids = []

    for idx, row in df.iterrows():
        mid = row['id']
        if mid in user_weights:
            interacted_indices.append(idx)
            interacted_weights.append(user_weights[mid])
            interacted_ids.append(mid)

    # Cold start: if user has no interactions yet, return top rated movies
    if not interacted_indices:
        # Sort by rating descending
        df_sorted = df.sort_values(by='rating', ascending=False)
        recs = df_sorted.head(limit).to_dict('records')
        for idx, r in enumerate(recs):
            r['match_score'] = f"{max(85, 96 - idx * 2)}% Match"
            genres_list = r.get('genres', [])
            genre_name = genres_list[0] if isinstance(genres_list, list) and genres_list else "Popular"
            r['ai_reason'] = f"Top Trending in {genre_name}"
            # Clean NaNs
            for k, v in list(r.items()):
                if not isinstance(v, (list, tuple, np.ndarray)) and pd.isna(v):
                    r[k] = None
        return recs

    # Build composite User Profile Vector
    # Sum weighted vectors of interacted movies
    user_profile_vec = np.zeros((1, tfidf_matrix.shape[1]))
    total_pos_weight = 0.0

    for idx, w in zip(interacted_indices, interacted_weights):
        vec = tfidf_matrix[idx].toarray()
        user_profile_vec += w * vec
        if w > 0:
            total_pos_weight += w

    if total_pos_weight > 0:
        norm = np.linalg.norm(user_profile_vec)
        if norm > 0:
            user_profile_vec = user_profile_vec / norm

    # Compute cosine similarity between user profile and all candidate movies
    cosine_sim = cosine_similarity(user_profile_vec, tfidf_matrix).flatten()

    # Blend with movie rating for quality: 80% similarity + 20% normalized rating
    ratings_normalized = df['rating'].fillna(7.0).values / 10.0
    final_scores = 0.80 * cosine_sim + 0.20 * ratings_normalized

    # Rank movies
    ranked = []
    for idx, score in enumerate(final_scores):
        mid = df.iloc[idx]['id']
        is_interacted = mid in interacted_ids
        
        # Calculate which specific interacted movie was closest for explanation
        best_sim = -1.0
        best_mid = None
        cand_vec = tfidf_matrix[idx]
        
        for i_idx, i_mid in zip(interacted_indices, interacted_ids):
            sim_with_item = cosine_similarity(cand_vec, tfidf_matrix[i_idx])[0][0]
            if sim_with_item > best_sim:
                best_sim = sim_with_item
                best_mid = i_mid

        # Determine AI explanation
        ai_reason = "Recommended for your taste"
        if best_mid and best_mid in source_reasons:
            action, title = source_reasons[best_mid]
            if not title:
                # Find title in df
                m_match = df[df['id'] == best_mid]
                if not m_match.empty:
                    title = m_match.iloc[0]['title']
                    
            if action == "liked":
                ai_reason = f"Because you liked {title}"
            elif action == "watched":
                ai_reason = f"Because you watched {title}"
            elif action == "watchlist":
                ai_reason = f"Similar to {title} on your watchlist"
            else:
                ai_reason = f"Matches your interest in {title}"
        else:
            # Use genre
            g_list = df.iloc[idx].get('genres', [])
            if isinstance(g_list, list) and g_list:
                ai_reason = f"Matches your taste in {g_list[0]}"

        # Calculate display match percentage (75% to 99%)
        sim_pct = int(min(99, max(75, 75 + score * 24)))
        match_score_str = f"{sim_pct}% Match"

        ranked.append({
            "index": idx,
            "id": mid,
            "score": score,
            "is_interacted": is_interacted,
            "match_score": match_score_str,
            "ai_reason": ai_reason
        })

    # Separate into unwatched and already watched
    unwatched = [item for item in ranked if not item['is_interacted']]
    watched = [item for item in ranked if item['is_interacted']]

    unwatched.sort(key=lambda x: x['score'], reverse=True)
    watched.sort(key=lambda x: x['score'], reverse=True)

    # Prioritize unwatched discoveries, but include top watched if catalog is small
    final_selected = unwatched[:limit]
    if len(final_selected) < limit:
        remaining = limit - len(final_selected)
        for w_item in watched[:remaining]:
            w_item['ai_reason'] = "Watch Again - High Match"
            final_selected.append(w_item)

    # Convert to movie dicts
    recs = []
    for item in final_selected:
        movie_dict = df.iloc[item['index']].to_dict()
        movie_dict['match_score'] = item['match_score']
        movie_dict['ai_reason'] = item['ai_reason']
        # Clean NaNs
        for k, v in list(movie_dict.items()):
            if not isinstance(v, (list, tuple, np.ndarray)) and pd.isna(v):
                movie_dict[k] = None
        recs.append(movie_dict)

    return recs

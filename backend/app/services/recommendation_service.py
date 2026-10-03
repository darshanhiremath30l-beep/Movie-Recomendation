import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..db import get_db

FALLBACK_MOVIES = [
    {
        "id": "tt12735488", 
        "title": "Kalki 2898 AD", 
        "genres": ["Sci-Fi", "Action"], 
        "synopsis": "When the world is consumed by darkness, a modern avatar descends to earth to protect the innocent from evil forces.", 
        "poster": "https://m.media-amazon.com/images/M/MV5BZjJhMTFiN2UtMmQ4MC00MTZjLTk3NDYtYWRkNTFmNDQwNDFjXkEyXkFqcGc@._V1_SX300.jpg"
    },
    {
        "id": "tt15239678", 
        "title": "Dune: Part Two", 
        "genres": ["Sci-Fi", "Adventure"], 
        "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.", 
        "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg"
    },
    {
        "id": "tt28448834", 
        "title": "Stree 2", 
        "genres": ["Horror", "Comedy"], 
        "synopsis": "The town of Chanderi is haunted again by a headless entity named Sarkata. Vicky and his squad must save their town.", 
        "poster": "https://m.media-amazon.com/images/M/MV5BMjA4Y2E4NDEtN2VhNC00NWMxLWEyNWItN2JjY2ZlNDI3NzQ1XkEyXkFqcGc@._V1_SX300.jpg"
    }
]

def fetch_movies():
    try:
        db = get_db()
        if db is not None:
            movies = list(db.movies.find({}, {"_id": 0}))
            if movies:
                return pd.DataFrame(movies)
    except Exception:
        pass
    return pd.DataFrame(FALLBACK_MOVIES)

def compute_recommendations_for_user(user_id):
    """
    Computes AI movie recommendations using multi-item TF-IDF vectorization 
    and Cosine Similarity calculated over user watch/like history in MongoDB Atlas.
    """
    df = fetch_movies()
    
    if df.empty:
        return FALLBACK_MOVIES
        
    movie_id_col = 'movie_id' if 'movie_id' in df.columns else 'id'
    
    # Standardize movie IDs
    df['id'] = df[movie_id_col]
    
    # Create combined features string (genres + synopsis)
    df['combined_features'] = df['genres'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x)) + ' ' + df['synopsis'].fillna('')
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
    
    try:
        db = get_db()
        if db is not None:
            # Query recent user interactions (watch, like, rate) sorted by newest first
            user_logs = list(db.interactions.find(
                {"user_id": user_id, "action_type": {"$in": ["watch", "like", "rate"]}}
            ).sort("timestamp", -1).limit(10))
            
            watched_ids = [log['movie_id'] for log in user_logs if 'movie_id' in log]
            
            if watched_ids:
                # Find indices of movies watched by user
                watched_indices = df.index[df['id'].isin(watched_ids)].tolist()
                
                if watched_indices:
                    # Compute average TF-IDF feature profile for user's watched movies
                    user_profile_vec = np.asarray(tfidf_matrix[watched_indices].mean(axis=0))
                    
                    # Cosine similarity between user profile vector and all candidate movies
                    cosine_sim = cosine_similarity(user_profile_vec, tfidf_matrix).flatten()
                    
                    # Sort candidates by similarity score in descending order
                    sim_scores = list(enumerate(cosine_sim))
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                    
                    # Filter out movies already watched by user unless database is small
                    unwatched_scores = [s for s in sim_scores if df.iloc[s[0]]['id'] not in watched_ids]
                    
                    # If unwatched candidates exist, select top 5; otherwise top 5 overall
                    top_indices = [s[0] for s in (unwatched_scores[:5] if unwatched_scores else sim_scores[:5])]
                    
                    recs = df.iloc[top_indices].to_dict('records')
                    
                    for r in recs:
                        for k, v in list(r.items()):
                            if not isinstance(v, (list, tuple, np.ndarray)) and pd.isna(v):
                                r[k] = None
                    return recs
    except Exception as e:
        print(f"Error computing AI recommendations: {e}")

    # Fallback to top rated movies
    recs = df.head(5).to_dict('records')
    for r in recs:
        for k, v in list(r.items()):
            if not isinstance(v, (list, tuple, np.ndarray)) and pd.isna(v):
                r[k] = None
    return recs



import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..db import get_db

FALLBACK_MOVIES = [
    {
        "id": "m1", 
        "title": "Neon Skyline", 
        "genres": ["Sci-Fi", "Action"], 
        "synopsis": "In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.", 
        "poster": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop"
    },
    {
        "id": "m2", 
        "title": "Echoes of Silence", 
        "genres": ["Drama", "Mystery"], 
        "synopsis": "A small-time detective unravels a deep mystery in a quiet coastal town where nothing is as it seems.", 
        "poster": "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=600&auto=format&fit=crop"
    },
    {
        "id": "m3", 
        "title": "Galactic Horizon", 
        "genres": ["Space", "Adventure"], 
        "synopsis": "Humanity's final attempt to find a new home leads a brave crew beyond the known boundaries of space.", 
        "poster": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=600&auto=format&fit=crop"
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
    Computes movie recommendations using TF-IDF and Cosine Similarity
    """
    df = fetch_movies()
    
    if df.empty:
        return FALLBACK_MOVIES
        
    movie_id_col = 'movie_id' if 'movie_id' in df.columns else 'id'
    
    # Create combined features
    df['combined_features'] = df['genres'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x)) + ' ' + df['synopsis'].fillna('')
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
    
    try:
        db = get_db()
        if db is not None:
            interactions = list(db.interactions.find({"user_id": user_id}).sort("timestamp", -1).limit(5))
            if interactions:
                latest_movie_id = interactions[0]['movie_id']
                movie_idx_series = df.index[df[movie_id_col] == latest_movie_id].tolist()
                    
                if movie_idx_series:
                    idx = movie_idx_series[0]
                    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix)
                    sim_scores = list(enumerate(cosine_sim[0]))
                    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                    # Start from 1 to avoid the movie itself
                    sim_scores = sim_scores[1:6]
                    
                    movie_indices = [i[0] for i in sim_scores]
                    recs = df.iloc[movie_indices].to_dict('records')
                    
                    for r in recs:
                        for k, v in list(r.items()):
                            if pd.isna(v):
                                r[k] = None
                        if movie_id_col == 'movie_id' and 'id' not in r:
                            r['id'] = r['movie_id']
                    return recs
    except Exception as e:
        print(f"Error computing recommendations: {e}")

    # Fallback to first 5
    recs = df.head(5).to_dict('records')
    for r in recs:
        for k, v in list(r.items()):
            if pd.isna(v):
                r[k] = None
        if movie_id_col == 'movie_id' and 'id' not in r:
            r['id'] = r['movie_id']
    return recs

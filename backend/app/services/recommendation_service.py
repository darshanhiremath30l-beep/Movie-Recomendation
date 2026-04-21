import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..db import get_db

FALLBACK_MOVIES = [
    {'id': 'm1', 'title': 'Neon Skyline', 'genres': ['Sci-Fi', 'Action'], 'synopsis': 'In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.', 'poster': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop'},
    {'id': 'm2', 'title': 'Echoes of Silence', 'genres': ['Drama', 'Mystery'], 'synopsis': 'A small-time detective unravels a deep mystery in a quiet coastal town where nothing is as it seems.', 'poster': 'https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=600&auto=format&fit=crop'},
    {'id': 'm3', 'title': 'Galactic Horizon', 'genres': ['Space', 'Adventure'], 'synopsis': 'Humanity\'s final attempt to find a new home leads a brave crew beyond the known boundaries of space.', 'poster': 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=600&auto=format&fit=crop'}
]

def fetch_movies():
    try:
        db = get_db()
        movies = list(db.movies.find({}, {'_id': 0}))
        if movies:
            return pd.DataFrame(movies)
    except Exception:
        pass
    return pd.DataFrame(FALLBACK_MOVIES)

def compute_recommendations_for_user(user_id):
    # Simple fallback implementation
    return FALLBACK_MOVIES

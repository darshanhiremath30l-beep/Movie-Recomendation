import os
import socket
import json
import urllib.request
import urllib.parse
from youtubesearchpython import VideosSearch

# Configure DNS to bypass ISP blocks on themoviedb.org in regions like India
try:
    import dns.resolver
    _dns_resolver = dns.resolver.Resolver()
    _dns_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
    _orig_getaddrinfo = socket.getaddrinfo

    def _custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if 'themoviedb.org' in host:
            try:
                answers = _dns_resolver.resolve(host, 'A')
                return _orig_getaddrinfo(answers[0].address, port, family, type, proto, flags)
            except Exception:
                pass
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = _custom_getaddrinfo
except Exception:
    pass

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '8265bd1679663a7ea12ac168da84d2e8').strip()
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_POSTER = 'https://image.tmdb.org/t/p/w500'
IMAGE_BASE_BACKDROP = 'https://image.tmdb.org/t/p/w1280'

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def format_tmdb_movie(item):
    """Normalize TMDB movie object to PopcornAI format."""
    if not item:
        return None

    genre_ids = item.get('genre_ids', [])
    genres = [GENRE_MAP.get(gid, "Cinema") for gid in genre_ids if gid in GENRE_MAP]
    if not genres:
        genres = ["Movie"]

    # Language tagging
    orig_lang = item.get('original_language', '')
    lang_labels = {'hi': 'Hindi', 'te': 'Telugu', 'ta': 'Tamil', 'kn': 'Kannada', 'ml': 'Malayalam'}
    if orig_lang in lang_labels:
        genres.insert(0, lang_labels[orig_lang])

    poster_path = item.get('poster_path')
    backdrop_path = item.get('backdrop_path')

    poster_url = f"{IMAGE_BASE_POSTER}{poster_path}" if poster_path else "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop"
    backdrop_url = f"{IMAGE_BASE_BACKDROP}{backdrop_path}" if backdrop_path else poster_url

    release_date = item.get('release_date', '')
    year = release_date[:4] if release_date else '2024'

    return {
        "id": f"tmdb_{item.get('id')}",
        "tmdb_id": item.get('id'),
        "title": item.get('title') or item.get('original_title') or 'Movie',
        "genres": genres,
        "rating": round(float(item.get('vote_average', 7.0)), 1),
        "year": year,
        "duration": "145m",
        "synopsis": item.get('overview') or "An exciting cinematic journey.",
        "poster": poster_url,
        "backdrop": backdrop_url,
        "cast": ["Popular Cast"],
        "director": "Acclaimed Director"
    }

def get_indian_movies(language='all', page=1):
    """
    Fetch trending & popular Indian movies across languages:
    Hindi (Bollywood), Telugu (Tollywood), Tamil (Kollywood), Kannada, Malayalam.
    """
    try:
        url = f"{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_origin_country=IN&sort_by=popularity.desc&page={page}"
        if language == 'hindi':
            url += "&with_original_language=hi"
        elif language == 'telugu':
            url += "&with_original_language=te"
        elif language == 'tamil':
            url += "&with_original_language=ta"
        elif language == 'kannada':
            url += "&with_original_language=kn"
        elif language == 'malayalam':
            url += "&with_original_language=ml"

        req = urllib.request.Request(url, headers={'User-Agent': 'PopcornAI/1.0'})
        with urllib.request.urlopen(req, timeout=2.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('results', [])
            return [format_tmdb_movie(m) for m in results if m.get('poster_path')]
    except Exception as e:
        print(f"Notice: TMDB get_indian_movies error: {e}")
        return []

def search_tmdb_movies(query):
    """Search movies using TMDB API with Indian titles priority."""
    if not query:
        return []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={encoded_query}&include_adult=false"
        req = urllib.request.Request(url, headers={'User-Agent': 'PopcornAI/1.0'})
        with urllib.request.urlopen(req, timeout=2.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('results', [])
            return [format_tmdb_movie(m) for m in results if m.get('poster_path')]
    except Exception as e:
        print(f"Notice: TMDB search error: {e}")
        return []


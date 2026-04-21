import requests
from youtubesearchpython import VideosSearch

OMDB_API_KEY = '46865f5b'
OMDB_BASE_URL = 'http://www.omdbapi.com/'

def parse_movie(movie_data):
    # Converts OMDB format to our internal dict format
    # Using 'imdbID' as our 'id' across the app
    if not movie_data or "Error" in movie_data:
        return None
        
    synopsis = movie_data.get('Plot', 'No synopsis available.')
    if synopsis == 'N/A': synopsis = 'No synopsis available.'
    
    genres = movie_data.get('Genre', '').split(', ')
    
    # parse rating
    rating = movie_data.get('imdbRating', '0.0')
    try:
        rating = float(rating)
    except:
        rating = 0.0

    poster = movie_data.get('Poster')
    if poster == 'N/A': poster = 'https://via.placeholder.com/600x900?text=No+Poster'
    
    return {
        "id": movie_data.get('imdbID'),
        "title": movie_data.get('Title'),
        "genres": genres,
        "rating": rating,
        "year": movie_data.get('Year'),
        "duration": movie_data.get('Runtime', '120m'),
        "synopsis": synopsis,
        "poster": poster,
        "backdrop": poster, # OMDB doesn't do backdrops natively
        "cast": movie_data.get('Actors', 'N/A').split(', '),
        "director": movie_data.get('Director', 'N/A'),
    }

def search_movies(query):
    try:
        res = requests.get(f"{OMDB_BASE_URL}?s={query}&apikey={OMDB_API_KEY}")
        data = res.json()
        if data.get("Response") == "True":
            results = []
            for item in data.get("Search", []):
                if item.get("Type") == "movie":
                    poster = item.get("Poster")
                    if poster == "N/A": poster = 'https://via.placeholder.com/600x900?text=No+Poster'
                    results.append({
                        "id": item.get('imdbID'),
                        "title": item.get('Title'),
                        "year": item.get('Year'),
                        "poster": poster,
                        # We guess placeholder fields since 's=' query lacks full detail
                        "genres": ["Movie"], 
                        "rating": 7.0,
                        "synopsis": "Click to view full details."
                    })
            return results
        return []
    except Exception as e:
        print(f"Error searching omdb: {e}")
        return []

def get_movie_details(imdb_id):
    try:
        res = requests.get(f"{OMDB_BASE_URL}?i={imdb_id}&plot=full&apikey={OMDB_API_KEY}")
        data = res.json()
        if data.get("Response") == "True":
            return parse_movie(data)
        return None
    except Exception as e:
        print(f"Error getting omdb details: {e}")
        return None

def get_trailer_url(movie_title):
    try:
        videosSearch = VideosSearch(f"{movie_title} official trailer", limit = 1)
        res = videosSearch.result()
        if res and 'result' in res and len(res['result']) > 0:
            link = res['result'][0]['link']
            # Convert normal link to embed link
            if "watch?v=" in link:
                video_id = link.split("watch?v=")[1].split("&")[0]
                return f"https://www.youtube.com/embed/{video_id}"
        return None
    except Exception as e:
        print(f"Trailer search error: {e}")
        return None

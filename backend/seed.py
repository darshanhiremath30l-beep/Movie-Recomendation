import os
import certifi
from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

MONGO_URI = os.getenv('MONGO_URI', '').strip()
MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'cinematch_db').strip()

mock_movies = [
  {
    "movie_id": "tt12735488",
    "title": "Kalki 2898 AD",
    "genres": ["Telugu", "Action", "Sci-Fi"],
    "rating": 7.6,
    "year": 2024,
    "duration": "3h 0m",
    "synopsis": "When the world is consumed by darkness, a modern avatar descends to earth to protect the innocent from evil forces in a futuristic post-apocalyptic world.",
    "poster": "https://m.media-amazon.com/images/M/MV5BZjJhMTFiN2UtMmQ4MC00MTZjLTk3NDYtYWRkNTFmNDQwNDFjXkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Prabhas", "Amitabh Bachchan", "Kamal Haasan", "Deepika Padukone"],
    "director": "Nag Ashwin"
  },
  {
    "movie_id": "tt15239678",
    "title": "Dune: Part Two",
    "genres": ["Sci-Fi", "Adventure", "Action"],
    "rating": 8.5,
    "year": 2024,
    "duration": "2h 46m",
    "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
    "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"],
    "director": "Denis Villeneuve"
  },
  {
    "movie_id": "tt28448834",
    "title": "Stree 2",
    "genres": ["Hindi", "Horror", "Comedy"],
    "rating": 7.5,
    "year": 2024,
    "duration": "2h 27m",
    "synopsis": "The town of Chanderi is haunted again by a headless entity named Sarkata. Vicky and his squad must save their town.",
    "poster": "https://m.media-amazon.com/images/M/MV5BMjA4Y2E4NDEtN2VhNC00NWMxLWEyNWItN2JjY2ZlNDI3NzQ1XkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Rajkummar Rao", "Shraddha Kapoor", "Pankaj Tripathi"],
    "director": "Amar Kaushik"
  },
  {
    "movie_id": "tt6263850",
    "title": "Deadpool & Wolverine",
    "genres": ["Action", "Comedy", "Sci-Fi"],
    "rating": 7.7,
    "year": 2024,
    "duration": "2h 8m",
    "synopsis": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool to defeat a common enemy.",
    "poster": "https://m.media-amazon.com/images/M/MV5BNzRiMjg0MzUtNTNhYi00N2Q5LWEwMzMtYWJiM2M1M2VkOGU1XkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Ryan Reynolds", "Hugh Jackman", "Emma Corrin"],
    "director": "Shawn Levy"
  },
  {
    "movie_id": "tt15398776",
    "title": "Oppenheimer",
    "genres": ["Drama", "History"],
    "rating": 8.9,
    "year": 2023,
    "duration": "3h 0m",
    "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
    "poster": "https://m.media-amazon.com/images/M/MV5BMDBmYTZjNjUtN2M1MS00MTQ2LTkNEtLTlhNzNhNmNhNTU0XkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
    "director": "Christopher Nolan"
  },
  {
    "movie_id": "tt15354916",
    "title": "Jawan",
    "genres": ["Hindi", "Action"],
    "rating": 7.0,
    "year": 2023,
    "duration": "2h 49m",
    "synopsis": "A prison warden recruits inmates to commit outrageous crimes that shed light on corruption and injustice.",
    "poster": "https://m.media-amazon.com/images/M/MV5BMGExNGI1NDktOWI2Mi00NDM3LWIxMmQtNTQxYTgzMzI0MTA1XkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Shah Rukh Khan", "Nayanthara", "Vijay Sethupathi"],
    "director": "Atlee"
  },
  {
    "movie_id": "tt8178634",
    "title": "RRR",
    "genres": ["Telugu", "Action"],
    "rating": 7.8,
    "year": 2022,
    "duration": "3h 7m",
    "synopsis": "A fearless warrior on a perilous mission comes face to face with a steely cop serving British forces in pre-independent India.",
    "poster": "https://m.media-amazon.com/images/M/MV5BNWMwODYyMjQtMTczMi00NTQ1LWFkYjItMGJhMWRkY2E3NDAyXkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1200&auto=format&fit=crop",
    "cast": ["N.T. Rama Rao Jr.", "Ram Charan", "Ajay Devgn"],
    "director": "S.S. Rajamouli"
  },
  {
    "movie_id": "tt10698680",
    "title": "K.G.F: Chapter 2",
    "genres": ["Kannada", "Action"],
    "rating": 8.2,
    "year": 2022,
    "duration": "2h 46m",
    "synopsis": "In the blood-soaked Kolar Gold Fields, Rocky's name strikes fear into his foes while he battles threats from all sides.",
    "poster": "https://m.media-amazon.com/images/M/MV5BZmQzZjVkZTUtYjI4ZC00ZDJmLWI0ZDUtZTFmMGM1Mzc5ZjIyXkEyXkFqcGc@._V1_SX300.jpg",
    "backdrop": "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Yash", "Sanjay Dutt", "Raveena Tandon"],
    "director": "Prashanth Neel"
  }
]

# Demo user credentials
mock_users = [
    {
        "_id": "650000000000000000000001",
        "name": "Demo User",
        "email": "demo@example.com",
        "password": generate_password_hash("password123"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "watchlist": ["tt12735488", "tt15239678"],
        "likes": ["tt15239678", "tt6263850"],
        "watch_history": ["tt15239678", "tt15398776"],
        "ratings": [
            {"movie_id": "tt15239678", "rating": 9.0}
        ]
    }
]

# Watchlist collection records
mock_watchlist = [
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt12735488",
        "title": "Kalki 2898 AD",
        "year": 2024,
        "poster": "https://m.media-amazon.com/images/M/MV5BZjJhMTFiN2UtMmQ4MC00MTZjLTk3NDYtYWRkNTFmNDQwNDFjXkEyXkFqcGc@._V1_SX300.jpg",
        "added_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt15239678",
        "title": "Dune: Part Two",
        "year": 2024,
        "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
        "added_at": datetime.now(timezone.utc).isoformat()
    }
]

# Liked movies collection records
mock_liked_movies = [
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt15239678",
        "title": "Dune: Part Two",
        "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
        "liked_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt6263850",
        "title": "Deadpool & Wolverine",
        "poster": "https://m.media-amazon.com/images/M/MV5BNzRiMjg0MzUtNTNhYi00N2Q5LWEwMzMtYWJiM2M1M2VkOGU1XkEyXkFqcGc@._V1_SX300.jpg",
        "liked_at": datetime.now(timezone.utc).isoformat()
    }
]

# Recently watched movies collection records
mock_recently_watched = [
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt15239678",
        "title": "Dune: Part Two",
        "duration": "2h 46m",
        "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
        "watched_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "user_id": "650000000000000000000001",
        "user_email": "demo@example.com",
        "movie_id": "tt15398776",
        "title": "Oppenheimer",
        "duration": "3h 0m",
        "poster": "https://m.media-amazon.com/images/M/MV5BMDBmYTZjNjUtN2M1MS00MTQ2LTkNEtLTlhNzNhNTU0XkEyXkFqcGc@._V1_SX300.jpg",
        "watched_at": datetime.now(timezone.utc).isoformat()
    }
]

def seed_db():
    placeholders = ["your-username", "your-password", "<username>", "<password>", "cluster-name", "<db_password>"]
    has_placeholder = any(p in MONGO_URI for p in placeholders)

    # Attempt seeding MongoDB Atlas / Server if configured
    if MONGO_URI and not has_placeholder:
        try:
            client_kwargs = {
                "serverSelectionTimeoutMS": 4000,
                "connectTimeoutMS": 4000
            }
            if "mongodb+srv://" in MONGO_URI or "ssl=true" in MONGO_URI.lower():
                client_kwargs["tlsCAFile"] = certifi.where()

            print(f"Connecting to MongoDB database '{MONGO_DBNAME}'...")
            client = MongoClient(MONGO_URI, **client_kwargs)
            client.admin.command('ping')
            db = client[MONGO_DBNAME]

            # 1. Movies table
            movies_coll = db['movies']
            movies_coll.delete_many({})
            res_m = movies_coll.insert_many(mock_movies)
            print(f"SUCCESS: 'movies' table seeded with {len(res_m.inserted_ids)} movies.")

            # 2. Users (Login credentials) table
            users_coll = db['users']
            users_coll.delete_many({})
            res_u = users_coll.insert_many(mock_users)
            try:
                users_coll.create_index([("email", ASCENDING)], unique=True)
            except Exception:
                pass
            print(f"SUCCESS: 'users' (login credentials) table seeded with {len(res_u.inserted_ids)} user (demo@example.com / password123).")

            # 3. Watchlist table
            wl_coll = db['watchlist']
            wl_coll.delete_many({})
            res_w = wl_coll.insert_many(mock_watchlist)
            try:
                wl_coll.create_index([("user_id", ASCENDING), ("movie_id", ASCENDING)], unique=True)
            except Exception:
                pass
            print(f"SUCCESS: 'watchlist' table seeded with {len(res_w.inserted_ids)} items.")

            # 4. Liked movies table
            likes_coll = db['liked_movies']
            likes_coll.delete_many({})
            res_l = likes_coll.insert_many(mock_liked_movies)
            try:
                likes_coll.create_index([("user_id", ASCENDING), ("movie_id", ASCENDING)], unique=True)
            except Exception:
                pass
            print(f"SUCCESS: 'liked_movies' table seeded with {len(res_l.inserted_ids)} items.")

            # 5. Recently watched table
            history_coll = db['recently_watched']
            history_coll.delete_many({})
            res_h = history_coll.insert_many(mock_recently_watched)
            try:
                history_coll.create_index([("user_id", ASCENDING), ("movie_id", ASCENDING)], unique=True)
            except Exception:
                pass
            print(f"SUCCESS: 'recently_watched' table seeded with {len(res_h.inserted_ids)} items.")

            print("\nALL 5 MongoDB collections/tables are ready to view in MongoDB Compass!")
            return
        except Exception as e:
            print(f"WARNING: MongoDB unavailable ({e}).")
    else:
        print("INFO: No valid external MONGO_URI found in backend/.env.")

    # Always ensure local JSON database is seeded as well
    try:
        from app.local_db import local_db
        local_db.movies.delete_many({})
        local_db.movies.insert_many(mock_movies)
        local_db.users.delete_many({})
        local_db.users.insert_many(mock_users)
        print("SUCCESS: Local JSON database seeded successfully with mock data!")
    except Exception as e:
        print(f"Error seeding local database: {e}")

if __name__ == '__main__':
    seed_db()

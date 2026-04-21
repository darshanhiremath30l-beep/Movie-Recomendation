import os
from pymongo import MongoClient

# Dummy config in case the main app config isn't available
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['cinematch']
movies_coll = db['movies']

mock_movies = [
  {
    "movie_id": "m1",
    "title": "Neon Skyline",
    "genres": ["Sci-Fi", "Action"],
    "rating": 8.7,
    "year": 2026,
    "duration": "2h 14m",
    "synopsis": "In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.",
    "poster": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Elena R.", "Marcus T.", "Sam K."],
    "director": "J. Cameron"
  },
  {
    "movie_id": "m2",
    "title": "Echoes of Silence",
    "genres": ["Drama", "Mystery"],
    "rating": 7.9,
    "year": 2025,
    "duration": "1h 58m",
    "synopsis": "A small-time detective unravels a deep mystery in a quiet coastal town where nothing is as it seems.",
    "poster": "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Sarah M.", "David O."],
    "director": "L. Villeneuve"
  },
  {
    "movie_id": "m3",
    "title": "Galactic Horizon",
    "genres": ["Space", "Adventure"],
    "rating": 9.1,
    "year": 2024,
    "duration": "2h 45m",
    "synopsis": "Humanity's final attempt to find a new home leads a brave crew beyond the known boundaries of space.",
    "poster": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Chris E.", "Anne H.", "Matthew M."],
    "director": "C. Nolan"
  },
  {
    "movie_id": "m4",
    "title": "The Cyber Heist",
    "genres": ["Thriller", "Crime"],
    "rating": 8.2,
    "year": 2025,
    "duration": "2h 5m",
    "synopsis": "A group of elite hackers plan the biggest digital bank robbery in history, but one of them has a hidden agenda.",
    "poster": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Tom H.", "Zendaya", "Florence P."],
    "director": "E. Wright"
  },
  {
    "movie_id": "m5",
    "title": "Whispering Shadows",
    "genres": ["Horror", "Thriller"],
    "rating": 6.8,
    "year": 2023,
    "duration": "1h 42m",
    "synopsis": "A family moves into an isolated mansion, only to discover the shadows hold terrifying secrets of the past.",
    "poster": "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Vera F.", "Patrick W."],
    "director": "J. Wan"
  },
  {
    "movie_id": "m6",
    "title": "Love in Kyoto",
    "genres": ["Romance", "Comedy"],
    "rating": 8.5,
    "year": 2026,
    "duration": "1h 52m",
    "synopsis": "Two strangers find themselves lost in Kyoto and discover love where they least expected it.",
    "poster": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Emma S.", "Ryan G."],
    "director": "D. Chazelle"
  },
  {
    "movie_id": "m7",
    "title": "Midnight Racer",
    "genres": ["Action", "Sports"],
    "rating": 7.4,
    "year": 2024,
    "duration": "2h 10m",
    "synopsis": "An underground street racer gets caught in a dangerous web of conspiracy and must win the ultimate race to survive.",
    "poster": "https://images.unsplash.com/photo-1541443131876-44b03de101c5?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1541443131876-44b03de101c5?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Vin D.", "Paul W."],
    "director": "J. Lin"
  },
  {
    "movie_id": "m8",
    "title": "The Last Kingdom",
    "genres": ["Fantasy", "Adventure"],
    "rating": 8.9,
    "year": 2025,
    "duration": "2h 55m",
    "synopsis": "A young prince must reclaim his stolen throne from a warlord using an army of mythical creatures.",
    "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=600&auto=format&fit=crop",
    "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop",
    "cast": ["Timothee C.", "Rebecca F."],
    "director": "P. Jackson"
  }
]

def seed_db():
    if movies_coll.count_documents({}) == 0:
        print("Seeding database with mock movies...")
        movies_coll.insert_many(mock_movies)
        print("Database seeded!")
    else:
        print("Database already contains movies. Skipping seed.")

if __name__ == '__main__':
    seed_db()

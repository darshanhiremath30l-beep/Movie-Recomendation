import os
import re
import json
import copy
import threading
from datetime import datetime, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash

class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class InsertManyResult:
    def __init__(self, inserted_ids):
        self.inserted_ids = inserted_ids

class MockCursor:
    def __init__(self, items, projection=None):
        self.items = copy.deepcopy(items)
        if projection:
            for item in self.items:
                for k in list(item.keys()):
                    if projection.get(k) == 0:
                        item.pop(k, None)

    def sort(self, key, direction=1):
        def sort_key(item):
            val = item.get(key)
            if val is None:
                return ""
            if isinstance(val, (int, float)):
                return val
            return str(val)
        self.items.sort(key=sort_key, reverse=(direction == -1))
        return self

    def limit(self, n):
        self.items = self.items[:n]
        return self

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

class LocalCollection:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    def _matches(self, doc, query):
        if not query:
            return True

        # Handle top-level $or
        if "$or" in query:
            subqueries = query["$or"]
            if not isinstance(subqueries, list):
                return False
            if not any(self._matches(doc, subq) for subq in subqueries):
                return False
            remaining = {k: v for k, v in query.items() if k != "$or"}
            if not remaining:
                return True
            return self._matches(doc, remaining)

        # Handle top-level $and
        if "$and" in query:
            subqueries = query["$and"]
            if not isinstance(subqueries, list):
                return False
            if not all(self._matches(doc, subq) for subq in subqueries):
                return False
            remaining = {k: v for k, v in query.items() if k != "$and"}
            if not remaining:
                return True
            return self._matches(doc, remaining)

        for key, val in query.items():
            doc_val = doc.get(key)

            # Handle ObjectId / id strings
            if key in ("_id", "id", "movie_id"):
                if str(doc_val or "") != str(val or ""):
                    return False
            elif key == "email":
                if str(doc_val or "").strip().lower() != str(val or "").strip().lower():
                    return False
            elif isinstance(val, dict):
                # Handle $regex
                if "$regex" in val:
                    pattern = val["$regex"]
                    options = val.get("$options", "")
                    flags = re.IGNORECASE if "i" in options else 0
                    try:
                        rx = re.compile(pattern, flags)
                    except Exception:
                        return False

                    if isinstance(doc_val, list):
                        if not any(isinstance(x, str) and rx.search(x) for x in doc_val):
                            return False
                    elif isinstance(doc_val, str):
                        if not rx.search(doc_val):
                            return False
                    else:
                        return False

                # Handle $in
                elif "$in" in val:
                    allowed = val["$in"]
                    if isinstance(doc_val, list):
                        if not any(item in allowed for item in doc_val):
                            return False
                    else:
                        if doc_val not in allowed:
                            return False

                # Handle $nin
                elif "$nin" in val:
                    disallowed = val["$nin"]
                    if isinstance(doc_val, list):
                        if any(item in disallowed for item in doc_val):
                            return False
                    else:
                        if doc_val in disallowed:
                            return False

                # Handle $eq
                elif "$eq" in val:
                    target = val["$eq"]
                    if isinstance(doc_val, list):
                        if target not in doc_val:
                            return False
                    elif doc_val != target:
                        return False

                # Handle $ne
                elif "$ne" in val:
                    target = val["$ne"]
                    if isinstance(doc_val, list):
                        if target in doc_val:
                            return False
                    elif doc_val == target:
                        return False
            else:
                # Direct equality or element in list
                if isinstance(doc_val, list):
                    if val not in doc_val and not any(str(x).lower() == str(val).lower() for x in doc_val):
                        return False
                else:
                    if doc_val != val:
                        return False

        return True

    def find_one(self, query=None):
        with self.db.lock:
            data = self.db._get_collection_data(self.name)
            for doc in data:
                if self._matches(doc, query):
                    return copy.deepcopy(doc)
            return None

    def find(self, query=None, projection=None):
        with self.db.lock:
            data = self.db._get_collection_data(self.name)
            matched = [doc for doc in data if self._matches(doc, query)]
            return MockCursor(matched, projection)

    def count_documents(self, query=None):
        with self.db.lock:
            data = self.db._get_collection_data(self.name)
            return sum(1 for doc in data if self._matches(doc, query))

    def insert_one(self, doc):
        with self.db.lock:
            doc_copy = copy.deepcopy(doc)
            if "_id" not in doc_copy or not doc_copy["_id"]:
                doc_copy["_id"] = str(ObjectId())
            else:
                doc_copy["_id"] = str(doc_copy["_id"])
            data = self.db._get_collection_data(self.name)
            data.append(doc_copy)
            self.db._save()
            return InsertOneResult(doc_copy["_id"])

    def insert_many(self, docs):
        with self.db.lock:
            data = self.db._get_collection_data(self.name)
            inserted_ids = []
            for doc in docs:
                doc_copy = copy.deepcopy(doc)
                if "_id" not in doc_copy or not doc_copy["_id"]:
                    doc_copy["_id"] = str(ObjectId())
                else:
                    doc_copy["_id"] = str(doc_copy["_id"])
                data.append(doc_copy)
                inserted_ids.append(doc_copy["_id"])
            self.db._save()
            return InsertManyResult(inserted_ids)

    def update_one(self, query, update):
        with self.db.lock:
            data = self.db._get_collection_data(self.name)
            for doc in data:
                if self._matches(doc, query):
                    if "$set" in update:
                        for k, v in update["$set"].items():
                            doc[k] = v
                    if "$addToSet" in update:
                        for k, v in update["$addToSet"].items():
                            if k not in doc or not isinstance(doc[k], list):
                                doc[k] = []
                            if v not in doc[k]:
                                doc[k].append(v)
                    if "$pull" in update:
                        for k, v in update["$pull"].items():
                            if k in doc and isinstance(doc[k], list):
                                doc[k] = [x for x in doc[k] if x != v]
                    self.db._save()
                    return {"matched": 1, "modified": 1}
            return {"matched": 0, "modified": 0}

    def delete_many(self, query=None):
        with self.db.lock:
            if not query:
                self.db.storage[self.name] = []
                self.db._save()
                return {"deleted_count": len(self.db.storage[self.name])}
            data = self.db._get_collection_data(self.name)
            original_len = len(data)
            self.db.storage[self.name] = [d for d in data if not self._matches(d, query)]
            self.db._save()
            return {"deleted_count": original_len - len(self.db.storage[self.name])}

class LocalDatabase:
    """
    Thread-safe, file-persisted mock database for offline development
    and seamless fallback when MongoDB Atlas credentials are not available.
    """
    def __init__(self, file_path=None):
        self.lock = threading.Lock()
        if not file_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            self.file_path = os.path.join(data_dir, 'local_db.json')
        else:
            self.file_path = file_path
        self.storage = {
            "users": [],
            "movies": [],
            "interactions": [],
            "watchlist": [],
            "ratings": []
        }
        self.collections = {}
        self._load()

    def _load(self):
        with self.lock:
            if os.path.exists(self.file_path):
                try:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        self.storage = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load local_db.json: {e}")
            self._ensure_defaults()

    def _ensure_defaults(self):
        for col in ["users", "movies", "interactions", "watchlist", "ratings"]:
            if col not in self.storage:
                self.storage[col] = []

        # Populate initial demo user if users collection is empty
        if not self.storage["users"]:
            demo_user = {
                "_id": "650000000000000000000001",
                "name": "Demo User",
                "email": "demo@example.com",
                "password": generate_password_hash("password123"),
                "watchlist": ["tt12735488", "tt15239678"],
                "likes": ["tt15239678"],
                "ratings": [{"movie_id": "tt15239678", "rating": 9.0}],
                "watch_history": []
            }
            # Pre-add darshan user matching credentials from .env for convenience
            dar_user = {
                "_id": "650000000000000000000002",
                "name": "Darshan",
                "email": "darshan@example.com",
                "password": generate_password_hash("keershana1930"),
                "watchlist": ["tt12735488", "tt28448834"],
                "likes": ["tt12735488"],
                "ratings": [],
                "watch_history": []
            }
            self.storage["users"] = [demo_user, dar_user]

        # Populate initial movies if movies collection is empty
        if not self.storage["movies"]:
            self.storage["movies"] = [
                {
                    "_id": "tt12735488",
                    "movie_id": "tt12735488",
                    "title": "Kalki 2898 AD",
                    "genres": ["Telugu", "Action", "Sci-Fi"],
                    "rating": 7.6,
                    "year": 2024,
                    "duration": "3h 0m",
                    "synopsis": "When the world is consumed by darkness, a modern avatar descends to earth to protect the innocent from evil forces in a futuristic post-apocalyptic world.",
                    "poster": "https://image.tmdb.org/t/p/w500/rstcAnBeCkxNQjNp3YXrF6IP1tW.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/o8XSR1SONnjcsv84NRu6Mwsl5io.jpg",
                    "cast": ["Prabhas", "Amitabh Bachchan", "Kamal Haasan", "Deepika Padukone"],
                    "director": "Nag Ashwin"
                },
                {
                    "_id": "tt15239678",
                    "movie_id": "tt15239678",
                    "title": "Dune: Part Two",
                    "genres": ["Sci-Fi", "Adventure", "Action"],
                    "rating": 8.5,
                    "year": 2024,
                    "duration": "2h 46m",
                    "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                    "poster": "https://image.tmdb.org/t/p/w500/6izwz7rsy95ARzTR3poZ8H6c5pp.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/eZ239CUp1d6OryZEBPnO2n87gMG.jpg",
                    "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"],
                    "director": "Denis Villeneuve"
                },
                {
                    "_id": "tt28448834",
                    "movie_id": "tt28448834",
                    "title": "Stree 2",
                    "genres": ["Hindi", "Horror", "Comedy"],
                    "rating": 7.5,
                    "year": 2024,
                    "duration": "2h 27m",
                    "synopsis": "The town of Chanderi is haunted again by a headless entity named Sarkata. Vicky and his squad must save their town.",
                    "poster": "https://image.tmdb.org/t/p/w500/m2zXTuNPkywdYLyWlVyJZW2QOJH.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/u060S4drIWntmLeMDGe7mD0V6Jh.jpg",
                    "cast": ["Rajkummar Rao", "Shraddha Kapoor", "Pankaj Tripathi"],
                    "director": "Amar Kaushik"
                },
                {
                    "_id": "tt6263850",
                    "movie_id": "tt6263850",
                    "title": "Deadpool & Wolverine",
                    "genres": ["Action", "Comedy", "Sci-Fi"],
                    "rating": 7.7,
                    "year": 2024,
                    "duration": "2h 8m",
                    "synopsis": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool to defeat a common enemy.",
                    "poster": "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/by8z9Fe8y7p4jo2YlW2SZDnptyT.jpg",
                    "cast": ["Ryan Reynolds", "Hugh Jackman", "Emma Corrin"],
                    "director": "Shawn Levy"
                },
                {
                    "_id": "tt15398776",
                    "movie_id": "tt15398776",
                    "title": "Oppenheimer",
                    "genres": ["Drama", "History"],
                    "rating": 8.9,
                    "year": 2023,
                    "duration": "3h 0m",
                    "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
                    "poster": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/neeNHeXjMF5fXoCJRsOmkNGC7q.jpg",
                    "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
                    "director": "Christopher Nolan"
                },
                {
                    "_id": "tt15354916",
                    "movie_id": "tt15354916",
                    "title": "Jawan",
                    "genres": ["Hindi", "Action", "Thriller"],
                    "rating": 7.0,
                    "year": 2023,
                    "duration": "2h 49m",
                    "synopsis": "A prison warden recruits inmates to commit outrageous crimes that shed light on corruption and injustice.",
                    "poster": "https://image.tmdb.org/t/p/w500/jFt1gS4BGHlK8xt76Y81Alp4dbt.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/5LtSjMNw6j3LkG29Oa4O0iY5U8.jpg",
                    "cast": ["Shah Rukh Khan", "Nayanthara", "Vijay Sethupathi"],
                    "director": "Atlee"
                },
                {
                    "_id": "tt8178634",
                    "movie_id": "tt8178634",
                    "title": "RRR",
                    "genres": ["Telugu", "Action", "Drama"],
                    "rating": 7.8,
                    "year": 2022,
                    "duration": "3h 7m",
                    "synopsis": "A fearless warrior on a perilous mission comes face to face with a steely cop serving British forces in pre-independent India.",
                    "poster": "https://image.tmdb.org/t/p/w500/wE0I6efAW4cDDmZQWtwZMOW44EJ.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/i0Y0wP8H6SRgjr6QmuwbtQbS24D.jpg",
                    "cast": ["N.T. Rama Rao Jr.", "Ram Charan", "Ajay Devgn"],
                    "director": "S.S. Rajamouli"
                },
                {
                    "_id": "tt10698680",
                    "movie_id": "tt10698680",
                    "title": "K.G.F: Chapter 2",
                    "genres": ["Kannada", "Action", "Crime"],
                    "rating": 8.2,
                    "year": 2022,
                    "duration": "2h 46m",
                    "synopsis": "In the blood-soaked Kolar Gold Fields, Rocky's name strikes fear into his foes while he battles threats from all sides.",
                    "poster": "https://image.tmdb.org/t/p/w500/khNVygolU0TxLIDWff5tQlAhZ23.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/nsV5Mfi9FAV4w8eDsdr7uqVswOk.jpg",
                    "cast": ["Yash", "Sanjay Dutt", "Raveena Tandon"],
                    "director": "Prashanth Neel"
                },
                {
                    "_id": "tt23849204",
                    "movie_id": "tt23849204",
                    "title": "12th Fail",
                    "genres": ["Hindi", "Drama", "Biography"],
                    "rating": 8.9,
                    "year": 2023,
                    "duration": "2h 27m",
                    "synopsis": "Based on the real-life story of IPS Officer Manoj Kumar Sharma, who fearlessly restarts his academic journey.",
                    "poster": "https://image.tmdb.org/t/p/w500/wTnV3PCVW5O92JMrFvvrRcV39RU.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/1pmXyN3sKeYoUhu5VBZiDU4BX21.jpg",
                    "cast": ["Vikrant Massey", "Medha Shankr", "Anant Joshi"],
                    "director": "Vidhu Vinod Chopra"
                },
                {
                    "_id": "tt15327088",
                    "movie_id": "tt15327088",
                    "title": "Kantara",
                    "genres": ["Kannada", "Action", "Drama"],
                    "rating": 8.2,
                    "year": 2022,
                    "duration": "2h 28m",
                    "synopsis": "When greed paves the way for betrayal and murder, a young tribal man embodies the spirit of his ancestors to seek divine justice.",
                    "poster": "https://image.tmdb.org/t/p/w500/jIsKmkxMzdCZ0Ux1GVSnu8m6Na6.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/kXElm7wt2kAXEVwJqW4cFhP43nW.jpg",
                    "cast": ["Rishab Shetty", "Sapthami Gowda", "Kishore"],
                    "director": "Rishab Shetty"
                },
                {
                    "_id": "tt9389998",
                    "movie_id": "tt9389998",
                    "title": "Pushpa: The Rise",
                    "genres": ["Telugu", "Action", "Crime"],
                    "rating": 7.6,
                    "year": 2021,
                    "duration": "2h 59m",
                    "synopsis": "A laborer rises through the ranks of a red sandalwood smuggling syndicate in the Seshachalam hills of Andhra Pradesh.",
                    "poster": "https://image.tmdb.org/t/p/w500/h6Pd89ngvl9quPVsx3KoJlQsvk9.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/jQIcn51nsvMrpB9NFwEOb9QHhFt.jpg",
                    "cast": ["Allu Arjun", "Rashmika Mandanna", "Fahadh Faasil"],
                    "director": "Sukumar"
                },
                {
                    "_id": "tt1375666",
                    "movie_id": "tt1375666",
                    "title": "Inception",
                    "genres": ["Sci-Fi", "Action", "Adventure"],
                    "rating": 8.8,
                    "year": 2010,
                    "duration": "2h 28m",
                    "synopsis": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                    "poster": "https://image.tmdb.org/t/p/w500/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg",
                    "backdrop": "https://image.tmdb.org/t/p/w1280/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
                    "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
                    "director": "Christopher Nolan"
                }
            ]
        self._save_unlocked()

    def _get_collection_data(self, name):
        if name not in self.storage:
            self.storage[name] = []
        return self.storage[name]

    def _save_unlocked(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.storage, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save local_db.json: {e}")

    def _save(self):
        self._save_unlocked()

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = LocalCollection(self, name)
        return self.collections[name]

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return self[name]

    def list_collection_names(self):
        return list(self.storage.keys())

    def create_collection(self, name):
        with self.lock:
            if name not in self.storage:
                self.storage[name] = []
                self._save()
        return self[name]

    def command(self, cmd, *args, **kwargs):
        if cmd == 'ping':
            return {'ok': 1.0}
        return {'ok': 1.0}

# Global singleton local database instance
local_db = LocalDatabase()

import time
import certifi
from pymongo import MongoClient
from flask import current_app
from bson import ObjectId
from .local_db import local_db

_mongo_client = None
_mongo_db = None
_mongo_available = None
_last_check_time = 0
RETRY_INTERVAL = 60  # Retry real MongoDB at most once per minute if unavailable

def is_valid_mongo_uri(uri):
    """Check if the MongoDB URI is non-empty and not an unfilled placeholder."""
    if not uri or not isinstance(uri, str):
        return False
    uri = uri.strip()
    if not (uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")):
        return False
    # Common placeholder markers
    placeholders = ["your-username", "your-password", "<username>", "<password>", "cluster-name", "<db_password>"]
    for ph in placeholders:
        if ph in uri:
            return False
    return True

def get_db():
    """
    Establish or return the active database connection.
    If MongoDB (Atlas or local) is reachable, returns the MongoDB database.
    If MongoDB is unconfigured or unreachable (bad auth, network error, or offline),
    seamlessly falls back to local_db (persistent JSON storage)
    without freezing API requests with repeated timeouts.
    """
    global _mongo_client, _mongo_db, _mongo_available, _last_check_time
    now = time.time()

    # If MongoDB was successfully connected, return it
    if _mongo_available is True and _mongo_db is not None:
        return _mongo_db

    # If MongoDB previously failed, avoid blocking every request; use local_db
    if _mongo_available is False and (now - _last_check_time < RETRY_INTERVAL):
        return local_db

    _last_check_time = now
    try:
        mongo_uri = current_app.config.get('MONGO_URI') if current_app else None
        db_name = current_app.config.get('MONGO_DBNAME', 'cinematch_db') if current_app else 'cinematch_db'

        if not is_valid_mongo_uri(mongo_uri):
            if _mongo_available is None:
                print("INFO: No external MongoDB URI configured in backend/.env.")
                print("INFO: CineMatch is operating in local persistent storage mode (backend/data/local_db.json).")
            _mongo_available = False
            return local_db

        client_kwargs = {
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 3000
        }
        if "mongodb+srv://" in mongo_uri or "ssl=true" in mongo_uri.lower() or "tls=true" in mongo_uri.lower():
            client_kwargs["tlsCAFile"] = certifi.where()

        client = MongoClient(mongo_uri, **client_kwargs)
        # Test the connection
        client.admin.command('ping')
        _mongo_client = client
        _mongo_db = client[db_name]
        _mongo_available = True
        print(f"OK: Connected to MongoDB database '{db_name}' successfully!")
        return _mongo_db
    except Exception as conn_error:
        if _mongo_available is not False:
            print(f"WARNING: MongoDB connection failed: {conn_error}")
            print("INFO: Falling back to local persistent storage mode (backend/data/local_db.json).")
        _mongo_available = False
        return local_db

def is_mongo_active():
    """Returns True if the current active database is real MongoDB."""
    return _mongo_available is True

def get_collection(collection_name):
    """Helper to get a collection from the active database."""
    db = get_db()
    if db is None:
        return local_db[collection_name]
    return db[collection_name]

def close_db(e=None):
    """Teardown handler. MongoClient handles its own connection pooling."""
    pass

def init_app(app):
    """Register database teardown and ensure collections exist."""
    app.teardown_appcontext(close_db)
    
    with app.app_context():
        try:
            db = get_db()
            collections = ['users', 'movies', 'watchlist', 'ratings', 'interactions']
            existing = db.list_collection_names()
            for collection_name in collections:
                if collection_name not in existing:
                    db.create_collection(collection_name)
            if _mongo_available:
                print("OK: MongoDB collections verified.")
            else:
                print("OK: Local JSON database collections initialized.")
        except Exception as e:
            print(f"WARNING: Collection initialization notice: {e}")

def serialize_doc(doc):
    """
    Recursively converts MongoDB ObjectIds and datetime objects to strings so they can be JSON serialized.
    """
    if not doc:
        return doc
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif hasattr(v, 'isoformat'):
                new_doc[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                new_doc[k] = serialize_doc(v)
            else:
                new_doc[k] = v
        return new_doc
    return doc

# Collection accessor functions
def get_users_collection():
    return get_collection('users')

def get_movies_collection():
    return get_collection('movies')

def get_ratings_collection():
    return get_collection('ratings')

def get_watchlist_collection():
    return get_collection('watchlist')

def get_interactions_collection():
    return get_collection('interactions')

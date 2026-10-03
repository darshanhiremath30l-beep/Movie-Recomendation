from pymongo import MongoClient
from flask import current_app, g
from bson import ObjectId
import os

def get_db():
    """
    Establish a connection to the MongoDB database.
    Reuses the connection globally within the request context logic.
    """
    if 'db' not in g:
        try:
            # Connect using the URI (PyMongo handles SSL/TLS automatically)
            client = MongoClient(
                current_app.config['MONGO_URI'],
                serverSelectionTimeoutMS=5000
            )
            # Test the connection
            client.admin.command('ping')
            g.client = client
            g.db = client[current_app.config['MONGO_DBNAME']]
            print("OK: MongoDB connected successfully")
        except Exception as conn_error:
            print(f"WARNING: MongoDB connection failed completely: {conn_error}")
            # Create a mock client for development
            g.client = None
            g.db = None
            print("WARNING: Using offline mode - database operations will be simulated")
    return g.db

def get_collection(collection_name):
    """Helper to get a collection from the database."""
    db = get_db()
    if db is None:
        return None  # Offline mode
    return db[collection_name]

def close_db(e=None):
    """Closes the connection after the request."""
    client = g.pop('client', None)
    if client is not None:
        client.close()

def init_app(app):
    """Register database teardown with the Flask app."""
    app.teardown_appcontext(close_db)
    
    # Initialize collections on app startup (with error handling)
    with app.app_context():
        try:
            db = get_db()
            if db is not None:
                # Ensure collections exist
                collections = ['users', 'movies', 'watchlist', 'ratings', 'interactions']
                for collection_name in collections:
                    if collection_name not in db.list_collection_names():
                        db.create_collection(collection_name)
                print("OK: MongoDB Connected - All collections initialized")
            else:
                print("WARNING: Database unavailable - starting in offline mode")
        except Exception as e:
            print(f"WARNING: MongoDB connection warning: {e}")
            print("WARNING: Flask app will continue without database connection")
            print("WARNING: Check your MongoDB Atlas connection string and network access")

def serialize_doc(doc):
    """
    Recursively converts MongoDB ObjectIds to strings so they can be JSON serialized.
    Use this wrapping any dict or list of dicts fetched from MongoDB.
    """
    if not doc:
        return doc
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            # Convert ObjectId to string
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
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

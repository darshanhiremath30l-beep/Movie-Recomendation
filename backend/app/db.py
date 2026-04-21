from pymongo import MongoClient
from flask import current_app, g
from bson import ObjectId

memory_interactions = []

def get_db():
    """
    Establish a connection to the MongoDB database.
    Reuses the connection globally within the request context logic.
    """
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.client = client
        g.db = client[current_app.config['MONGO_DBNAME']]
    return g.db

def close_db(e=None):
    """Closes the connection after the request."""
    client = g.pop('client', None)
    if client is not None:
        client.close()

def init_app(app):
    """Register database teardown with the Flask app."""
    app.teardown_appcontext(close_db)

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

# Beginner-friendly collection helpers
def get_users_collection():
    return get_db().users

def get_movies_collection():
    return get_db().movies

def get_ratings_collection():
    return get_db().ratings

def get_watchlist_collection():
    return get_db().watchlist

def get_watch_history_collection():
    return get_db().watch_history

def get_recommendations_collection():
    return get_db().recommendations

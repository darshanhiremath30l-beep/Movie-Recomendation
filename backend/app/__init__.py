from flask import Flask
from flask_cors import CORS
from .config import config_dict

def create_app(config_name='default'):
    """App factory method to initialize the Flask application."""
    app = Flask(__name__)
    
    # Load settings from config
    app.config.from_object(config_dict[config_name])
    
    # Initialize basic CORS so the React frontend can contact this API
    CORS(app)
    
    # Initialize DB connection handlers
    from .db import init_app as init_db, get_db, is_mongo_active
    init_db(app)
    
    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.movies import movies_bp
    from .routes.users import users_bp
    from .routes.recommendations import recommendations_bp
    from .routes.interactions import interactions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')

    # Basic root endpoint check
    @app.route('/api/health')
    def health_check():
        db = get_db()
        if is_mongo_active():
            db_status = "mongodb_connected"
            db_type = "MongoDB Server / Atlas"
        else:
            db_status = "local_storage_mode"
            db_type = "Local JSON Storage (local_db.json)"
            
        return {
            'status': 'healthy', 
            'message': 'PopcornAI API is running!',
            'db_status': db_status,
            'database_type': db_type
        }
        
    return app

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
    from .db import init_app as init_db, get_db
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
        db_status = "disconnected"
        try:
            # Ping database to verify connection
            get_db().command('ping')
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
            
        return {
            'status': 'healthy', 
            'message': 'CineMatch AI API is running!',
            'db_status': db_status
        }
        
    return app

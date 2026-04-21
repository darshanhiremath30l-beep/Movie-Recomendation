import os
from app import create_app

# Use 'development' config by default unless set
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Run the Flask app on local port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)

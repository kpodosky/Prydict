from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Import routes after app creation to avoid circular imports
    from Prydict.app import routes
    
    # Register blueprints if you have any
    # app.register_blueprint(some_blueprint)
    
    return app

# Create the application instance
app = create_app()
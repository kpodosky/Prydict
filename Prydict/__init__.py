from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
from queue import Queue

# Initialize queue for whale tracking
transaction_queue = Queue(maxsize=100)
whale_tracker = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Import routes after app creation to avoid circular imports
    from Prydict import routes
    
    # Register routes
    app.add_url_rule('/', 'index', routes.index)
    app.add_url_rule('/predict_btc', 'predict_btc', routes.predict_btc, methods=['POST'])
    app.add_url_rule('/predict_eth', 'predict_eth', routes.predict_eth, methods=['POST'])
    app.add_url_rule('/predict_usdc', 'predict_usdc', routes.predict_usdc, methods=['POST'])
    app.add_url_rule('/predict_usdt', 'predict_usdt', routes.predict_usdt, methods=['POST'])
    app.add_url_rule('/whale_watch', 'whale_watch', routes.whale_watch, methods=['POST'])
    app.add_url_rule('/api/whale-transactions', 'get_whale_transactions', routes.get_whale_transactions)
    
    return app

# Create the application instance
app = create_app()
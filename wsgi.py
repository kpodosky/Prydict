import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Prydict import create_app

# Create the application instance with environment config
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
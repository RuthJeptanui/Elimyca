from flask import Flask
from routes import main_bp
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Set secret key - prioritize environment variable, fallback to config or default
    app.secret_key = os.environ.get('SECRET_KEY') 
    
    # If no environment variable, try to use config (but config might not have it either)
    if not app.secret_key:
        try:
            import config
            app.secret_key = getattr(config, 'SECRET_KEY', 'dev-key-for-development-only')
        except ImportError:
            app.secret_key = 'dev-key-for-development-only'
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
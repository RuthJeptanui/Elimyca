from flask import Flask
import config
from routes import main_bp
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key'
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
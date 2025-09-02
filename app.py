from flask import Flask
import config
from routes import main_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
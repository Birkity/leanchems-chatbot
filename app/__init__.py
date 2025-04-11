from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .routes import bp

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    CORS(app)
    load_dotenv()

    # Register the blueprint
    app.register_blueprint(bp)

    return app
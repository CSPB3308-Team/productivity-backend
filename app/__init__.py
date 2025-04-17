import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize SQLAlchemy but don't bind it to the app yet
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("FRONTEND_URL"), supports_credentials=True)

    # Read environment flag (default to "local" if not set)
    app_env = os.getenv("APP_ENV", "local").lower()

    if app_env == "production":
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required in production")
    elif app_env == "docker":
        database_url = os.getenv("DOCKER_DATABASE_URL")
    else:  # local
        database_url = os.getenv("LOCAL_DATABASE_URL")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # Load database config
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = app_env == "testing"

    # Bind database to the app
    db.init_app(app)
    Migrate(app, db)

    # Import models AFTER initializing db
    from app import models

    # Import and register blueprints (routes)
    from app.routes import main
    app.register_blueprint(main)

    return app

# Init app
app = create_app()

print(f"⚡ Running in {os.getenv('APP_ENV', 'local').upper()} mode")
print(f"🔌 Connected to database: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"🌍 Running on http://0.0.0.0:{os.getenv('FLASK_RUN_PORT', '3308')}")

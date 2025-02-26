import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize SQLAlchemy but don't bind it to the app yet
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Read environment flag (default to "local" if not set)
    app_env = os.getenv("APP_ENV", "local").lower()

    # Switch between docker and local machine
    if app_env == "docker":
        database_url = os.getenv("DOCKER_DATABASE_URL", "postgresql://postgres:password@db:5432/postgres")
    else:
        database_url = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:password@localhost:5432/taskagotchi")

    # Load configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

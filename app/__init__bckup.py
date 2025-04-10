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

    # Determine the correct database URL based on environment
    if app_env == "testing":
        database_url = "sqlite:///:memory:"
    elif app_env == "docker":
        database_url = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
        )
    else:  # default to local
        database_url = os.getenv(
            "LOCAL_DATABASE_URL",
            f"postgresql://{os.getenv('POSTGRES_USER', 'taskagotchi_user')}:" +
            f"{os.getenv('POSTGRES_PASSWORD', 'taskagotchi_password')}@localhost:" +
            f"{os.getenv('DB_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'taskagotchi_db')}"
        )

    # Load database config
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = app_env == "testing"

    # Debug info
    print(f"✅ Running in {app_env.upper()} mode")
    print(f"🔌 Connected to database: {database_url}")

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

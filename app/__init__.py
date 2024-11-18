from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(testing=False):
    """Create a Flask application with optional testing configuration."""
    app = Flask(__name__)

    # Use SQLite in-memory database for testing or PostgreSQL for normal operation
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin@localhost:5432/testing_db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = testing

    db.init_app(app)    
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    from .routes import main
    app.register_blueprint(main)

    return app

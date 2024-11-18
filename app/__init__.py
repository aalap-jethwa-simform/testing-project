from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()

def create_app(testing=False):
    """Create a Flask application with optional testing configuration."""
    app = Flask(__name__)
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://odoo:root@localhost:5432/test_db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://odoo:root@localhost:5432/flask_test_proj'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = testing

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    app.register_blueprint(main)

    return app

import pytest
from sqlalchemy import create_engine
from app import create_app, db


@pytest.fixture(scope="session")
def app():
    """Create a Flask app for testing with an in-memory SQLite database."""
    app = create_app(testing=True)

    # Update app config to use SQLite in-memory database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()  # Create tables in the in-memory database
        yield app
        db.session.remove()
        db.drop_all()  # Drop tables after the tests


@pytest.fixture(scope="module")
def client(app):
    """Provide a test client for the app."""
    return app.test_client()


@pytest.fixture
def add_user():
    """Helper function to add a user to the database."""
    def _add_user(name, email):
        from app.models import User
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user
    return _add_user

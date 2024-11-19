import pytest
from app import create_app, db
from app.models import User


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
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise  # Re-raise the exception for the test to fail
        return user

    return _add_user


@pytest.fixture
def add_project():
    """Helper function to add a project to the database."""

    def _add_project(name, description, user_id):
        from app.models import Project
        project = Project(name=name,
                          description=description,
                          user_id=user_id)
        db.session.add(project)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise  # Re-raise the exception for the test to fail
        return project

    return _add_project
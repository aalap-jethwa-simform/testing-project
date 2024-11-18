import pytest
from sqlalchemy import create_engine
from app import create_app, db

# Admin connection to manage databases
ADMIN_DB_URI = "postgresql+psycopg2://odoo:root@localhost:5432/postgres"
TEST_DB_URI = "postgresql+psycopg2://odoo:root@localhost:5432/test_db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create the test database before tests and drop it afterward."""
    engine = create_engine(ADMIN_DB_URI)
    connection = engine.connect()
    connection.execution_options(isolation_level="AUTOCOMMIT")

    # Create the test database
    try:
        connection.execute("CREATE DATABASE test_db")
        print("Test database created successfully.")
    except Exception as e:
        print(f"Could not create test database. Error: {e}")

    yield  # Tests run here

    # Drop the test database
    try:
        connection.execute("DROP DATABASE IF EXISTS test_db")
        print("Test database dropped successfully.")
    except Exception as e:
        print(f"Could not drop test database. Error: {e}")

    connection.close()


@pytest.fixture(scope="module")
def app(setup_test_database):
    """Create a Flask app for testing."""
    app = create_app(testing=True)

    with app.app_context():
        db.create_all()  # Create tables in the test database
        yield app
        db.session.remove()
        db.drop_all()  # Drop tables after the tests


@pytest.fixture(scope='module')
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

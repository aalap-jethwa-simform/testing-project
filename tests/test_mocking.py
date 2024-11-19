import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from sqlalchemy.exc import IntegrityError

# Import the Flask app and components
from app.routes import main
from app.models import db, User


class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app and register the blueprint
        self.app = Flask(__name__)
        self.app.register_blueprint(main)
        self.client = self.app.test_client()

        # Push application context to use Flask's db and other components
        self.app.app_context().push()

    @patch('app.models.db.session')  # Patch the database session
    @patch('app.models.User')  # Patch the User model
    def test_create_user_success(self, mock_user, mock_session):
        # Mock User instance creation
        mock_user.return_value = MagicMock()

        # Mock session behavior
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        # Simulate a successful POST request
        response = self.client.post(
            '/users',
            json={"name": "John Doe", "email": "john@example.com"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json.get("message"), 'User created')

    @patch('app.models.db.session')
    @patch('app.models.User')
    def test_create_user_database_error(self, mock_user, mock_session):
        # Mock IntegrityError unrelated to unique constraint
        mock_session.commit.side_effect = IntegrityError(
            "Some other DB issue", None, None
        )

        # Simulate a POST request causing a database error
        response = self.client.post(
            '/users',
            json={"name": "Jane Doe", "email": "error@example.com"}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {'error': 'Database error occurred'})

    @patch('app.models.db.session')
    @patch('app.models.User')
    def test_create_user_internal_server_error(self, mock_user, mock_session):
        # Mock generic exception during commit
        mock_session.commit.side_effect = Exception("Unexpected error")

        # Simulate a POST request causing a generic exception
        response = self.client.post(
            '/users',
            json={"name": "Invalid User", "email": "invalid@example.com"}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {'error': 'Internal Server Error'})

    @patch('app.models.User.query')  # Patch the User query to mock data
    def test_get_users_success(self, mock_user_query):
        # Create mock user objects with mocked attributes
        mock_user_1 = MagicMock()
        mock_user_1.id = 1
        mock_user_1.name = "John Doe"
        mock_user_1.email = "john@example.com"

        mock_user_2 = MagicMock()
        mock_user_2.id = 2
        mock_user_2.name = "Jane Doe"
        mock_user_2.email = "jane@example.com"

        # Mock the return value of User.query.all() to return a list of users
        mock_user_query.all.return_value = [mock_user_1, mock_user_2]

        # Simulate a successful GET request
        response = self.client.get('/v2/users')

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the JSON response is as expected
        expected_json = [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane Doe', 'email': 'jane@example.com'}
        ]
        self.assertEqual(response.json, expected_json)

    @patch('app.models.User.query')  # Patch the User query to mock data
    def test_get_users_empty(self, mock_user_query):
        # Mock the return value of User.query.all() to return an empty list
        mock_user_query.all.return_value = []

        # Simulate a successful GET request with no users
        response = self.client.get('/v2/users')

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the JSON response is an empty list
        self.assertEqual(response.json, [])  # No users to return


if __name__ == '__main__':
    unittest.main()

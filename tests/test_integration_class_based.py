import pytest
from app.models import User, Project
from app import db


class TestUserIntegrationTest:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, client):
        """Setup and teardown for user tests."""
        User.query.delete()
        db.session.commit()
        self.client = client
        yield
        User.query.delete()
        db.session.commit()

    def test_home(self):
        """Test the home endpoint."""
        response = self.client.get('/')
        assert response.status_code == 200
        assert response.json == {'message': 'Welcome to the Flask App'}

    def test_create_user_success(self):
        """Test successful user creation."""
        user_data = {"name": "John Doe", "email": "john.doe@example.com"}
        response = self.client.post('/users', json=user_data)

        # Check that the status code is 201 (Created)
        assert response.status_code == 201

        # Check that the response contains the 'message' and 'id'
        response_json = response.json
        assert 'id' in response_json  # Ensure 'id' is in the response
        assert response_json['message'] == 'User created'

    def test_create_user_duplicate_email(self):
        """Test creating a user with a duplicate email."""
        user_data = {"name": "Jane Doe", "email": "jane.doe@example.com"}
        self.client.post('/users', json=user_data)
        duplicate_data = {"name": "John Doe", "email": "jane.doe@example.com"}
        response = self.client.post('/users', json=duplicate_data)
        assert response.status_code == 400
        assert response.json == {'message': 'User with this email already exists'}

    def test_create_user_missing_fields(self):
        """Test creating a user with missing fields."""
        incomplete_data = {"name": "John Doe"}
        response = self.client.post('/users', json=incomplete_data)
        assert response.status_code == 400
        assert response.json == {'error': 'Missing name or email'}

    def test_get_users_empty(self):
        """Test retrieving users when there are none."""
        response = self.client.get('/users')
        assert response.status_code == 200
        assert response.json == []

    def test_get_users_with_data(self):
        """Test retrieving users when users exist."""
        user_data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
        for user in user_data:
            self.client.post('/users', json=user)
        response = self.client.get('/users')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['name'] == "Alice"
        assert response.json[1]['name'] == "Bob"

    def test_update_user(self):
        """Test updating an existing user."""
        user_data = {"name": "John Doe", "email": "john.doe@example.com"}
        create_response = self.client.post('/users', json=user_data)
        user_id = create_response.json['id']

        updated_data = {"name": "John Updated", "email": "john.updated@example.com"}
        response = self.client.put(f'/users/{user_id}', json=updated_data)
        assert response.status_code == 200
        assert response.json == {'message': 'User updated'}

    def test_delete_user(self):
        """Test deleting an existing user."""
        user_data = {"name": "John Doe", "email": "john.doe@example.com"}
        create_response = self.client.post('/users', json=user_data)
        user_id = create_response.json['id']

        delete_response = self.client.delete(f'/users/{user_id}')
        assert delete_response.status_code == 200
        assert delete_response.json == {'message': 'User deleted'}


class TestProjectIntegrationTest:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, client, add_user, add_project):
        """Setup and teardown for project tests."""
        self.client = client
        self.add_user = add_user
        self.add_project = add_project
        User.query.delete()
        Project.query.delete()
        db.session.commit()
        yield
        User.query.delete()
        Project.query.delete()
        db.session.commit()

    def test_create_project_success(self):
        """Test successful project creation."""
        user = self.add_user(name="John Doe", email="john.doe@example.com")
        project_data = {"name": "Test Project", "description": "Test Desc", "user_id": user.id}
        response = self.client.post('/projects', json=project_data)
        assert response.status_code == 201
        assert 'project_id' in response.json

    def test_delete_project(self):
        """Test deleting a project."""
        user = self.add_user(name="John Doe", email="mokshit23@example.com")
        project = self.add_project(name="Project A", description="Description A", user_id=user.id)
        delete_response = self.client.delete(f'/projects/{project.id}')
        print(delete_response)
        assert delete_response.status_code == 200
        assert delete_response.json == {'message': 'Project deleted'}

    def test_create_project_with_unregistered_user(self):
        """Test creating a project with an unregistered user."""
        project_data = {"name": "Test Project", "description": "Description", "user_id": 999}
        response = self.client.post('/projects', json=project_data)
        assert response.status_code == 404
        assert response.json == {'error': 'User not found'}

    def test_get_projects_forbidden(self):
        """Test retrieving projects of another user."""
        user1 = self.add_user(name="Alice", email="alice@example.com")
        user2 = self.add_user(name="Bob", email="bob@example.com")
        project_data = {"name": "Project", "description": "Desc", "user_id": user1.id}
        self.client.post('/projects', json=project_data)
        response = self.client.get(f'/projects/{user1.id}', query_string={"current_user_id": user2.id})
        assert response.status_code == 403
        assert response.json == {'error': 'Forbidden: You can only access your projects'}

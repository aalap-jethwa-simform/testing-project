from app import db
from app.models import User


def test_get_users_empty(client):
    """Test retrieving users when there are none."""
    User.query.delete()
    db.session.commit()
    response = client.get('/users')
    assert response.status_code == 200


def test_home(client):
    """Test the home endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {'message': 'Welcome to the Flask App'}


def test_create_user_success(client):
    """Test successful user creation."""
    user_data = {"name": "John Doe", "email": "john.doe@example.com"}
    response = client.post('/users', json=user_data)

    assert response.status_code == 201
    assert response.json == {'message': 'User created'}


def test_create_user_duplicate_email(client, add_user):
    """Test creating a user with an existing email."""
    add_user(name="Jane Doe", email="jane.doe@example.com")  # Add a user with this email first

    duplicate_data = {"name": "John Doe", "email": "jane.doe@example.com"}
    response = client.post('/users', json=duplicate_data)
    assert response.status_code == 400
    assert response.json == {'message': 'User with this email already exists'}


def test_create_user_missing_fields(client):
    """Test user creation with missing fields."""
    incomplete_data = {"name": "John Doe"}  # Missing email
    response = client.post('/users', json=incomplete_data)

    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json == {'error': 'Missing name or email'}


def test_create_user_invalid_json(client):
    """Test user creation with invalid JSON payload."""
    invalid_data = "this is not JSON"
    response = client.post('/users', data=invalid_data)

    assert response.status_code == 500
    assert 'error' in response.json
    assert response.json['error'] == 'Internal Server Error'


def test_get_users_with_data(client, add_user):
    """Test retrieving users when users exist."""
    User.query.delete()
    db.session.commit()
    add_user(name="Alice", email="alice@example.com")
    add_user(name="Bob", email="bob@example.com")

    response = client.get('/users')
    assert response.status_code == 200

    # Verify all users are returned
    users = response.json
    assert len(users) == 2
    assert users[0]['name'] == "Alice"
    assert users[1]['name'] == "Bob"


def test_database_integrity_error_handling(client, mocker):
    """Test database error handling by mocking a commit failure."""
    mocker.patch('app.db.session.commit', side_effect=Exception("DB Error"))

    user_data = {"name": "John Doe", "email": "john.doe@example.com"}
    response = client.post('/users', json=user_data)

    assert response.status_code == 500
    assert 'error' in response.json
    assert response.json['error'] == 'Internal Server Error'


''' Project Module Testcases'''


def test_create_project_with_unregistered_user(client):
    """Test creating a project with an unregistered user should return 403."""
    project_data = {"name": "Test Project", "description": "Description", "user_id": 999}  # Non-existent user
    response = client.post('/projects', json=project_data)
    assert response.status_code == 403
    assert response.json == {'error': 'User not found'}


def test_create_project_success(client, add_user):
    """Test creating a project with a valid registered user."""
    user = add_user(name="John Doe", email="john.doe@example.com")
    project_data = {"name": "Test Project", "description": "Description", "user_id": user.id}
    response = client.post('/projects', json=project_data)
    assert response.status_code == 201
    assert 'project_id' in response.json


def test_get_projects_unauthorized(client, add_user):
    """Test getting projects when unauthorized should return 403."""
    user = add_user(name="John Doe", email="mokshit@example.com")
    response = client.get(f'/projects/{user.id}')
    assert response.status_code == 403
    assert response.json == {'error': 'Unauthorized'}


def test_get_projects_forbidden(client, add_user):
    """Test getting projects for another user should return 403."""
    user1 = add_user(name="John Doe", email="aalap@example.com")
    user2 = add_user(name="Jane Smith", email="mitang@example.com")

    # Create a project for user1
    client.post('/projects', json={"name": "Project A", "description": "Test Project", "user_id": user1.id})

    # Attempt to get user1's projects as user2
    response = client.get(f'/projects/{user1.id}', query_string={"current_user_id": user2.id})
    assert response.status_code == 403
    assert response.json == {'error': 'Forbidden: You can only access your projects'}


def test_get_projects_success(client, add_user):
    """Test getting projects for an authorized user."""
    user = add_user(name="John Doe", email="deepak@example.com")

    # Create projects for the user
    client.post('/projects', json={"name": "Project A", "description": "Test Project A", "user_id": user.id})
    client.post('/projects', json={"name": "Project B", "description": "Test Project B", "user_id": user.id})

    response = client.get(f'/projects/{user.id}', query_string={"current_user_id": user.id})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['name'] == 'Project A'
    assert response.json[1]['name'] == 'Project B'

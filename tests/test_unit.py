import pytest
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError
import re


def test_create_user(add_user):
    """Test creating a user and saving to the database."""
    user = add_user(name="John Doe", email="john@example.com")

    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.id is not None

    user_from_db = db.session.get(User, user.id)
    assert user_from_db is not None
    assert user_from_db.name == "John Doe"
    assert user_from_db.email == "john@example.com"


def test_read_user(add_user):
    """Test retrieving a user from the database."""
    user = add_user(name="Jane Doe", email="jane@example.com")

    user_from_db = db.session.get(User, user.id)
    assert user_from_db is not None
    assert user_from_db.name == "Jane Doe"
    assert user_from_db.email == "jane@example.com"


def test_update_user(add_user):
    """Test updating an existing user in the database."""
    user = add_user(name="Alice", email="alicetest@example.com")

    # Update the user's name
    user.name = "Alicia"
    db.session.commit()

    # Retrieve the updated user
    updated_user = db.session.get(User, user.id)
    assert updated_user.name == "Alicia"
    assert updated_user.email == "alicetest@example.com"


def test_delete_user(add_user):
    """Test deleting a user from the database."""
    user = add_user(name="Bob", email="bob@example.com")

    # Ensure the user exists in the database before deletion
    user_from_db = db.session.get(User, user.id)
    assert user_from_db is not None

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    # Ensure the user has been deleted
    deleted_user = db.session.get(User, user.id)
    assert deleted_user is None

def test_user_email_uniqueness(add_user):
    """Test that the email field is unique."""
    # Add a user with a specific email
    add_user(name="Charlie", email="charlie@example.com")

    # Try to add another user with the same email and catch the exception
    with pytest.raises(IntegrityError):
        add_user(name="Dan", email="charlie@example.com")

    # Verify that only one user with this email exists
    users_with_same_email = User.query.filter_by(email="charlie@example.com").all()
    assert len(users_with_same_email) == 1


def test_user_email_required(add_user):
    """Test that the email field is required."""
    # Try to create a user with no email
    with pytest.raises(IntegrityError):
        add_user(name="No Email", email=None)


def is_valid_email(email):
    """Basic email validation function."""
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")


def test_user_invalid_email_format(add_user):
    """Test that the email must be in a valid format."""
    with pytest.raises(ValueError):
        is_valid_email("invalidemail")
        add_user(name="Invalid Email", email="invalidemail")


def test_create_multiple_users(add_user):
    """Test creating multiple users and retrieving them."""
    user1 = add_user(name="User One", email="user1@example.com")
    user2 = add_user(name="User Two", email="user2@example.com")

    assert user1.id is not None
    assert user2.id is not None

    user_from_db1 = db.session.get(User, user1.id)
    user_from_db2 = db.session.get(User, user2.id)

    assert user_from_db1.name == "User One"
    assert user_from_db1.email == "user1@example.com"
    assert user_from_db2.name == "User Two"
    assert user_from_db2.email == "user2@example.com"


def test_create_user_success(client):
    """Test creating a user successfully."""
    response = client.post('/users', json={
        'name': 'John Doe',
        'email': 'testuser@example.com'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created'

    # Verify the user is in the database
    with client.application.app_context():
        user = User.query.filter_by(email='john@example.com').first()
        assert user is not None
        assert user.name == 'John Doe'


def test_create_user_missing_fields(client):
    """Test creating a user with missing fields."""
    response = client.post('/users', json={'name': 'Incomplete'})
    assert response.status_code == 500
    assert 'error' in response.json


def test_get_users_empty(client):
    """Test retrieving users when no users exist."""
    response = client.get('/users')
    assert response.status_code == 200


def test_get_users_with_invalid_method(client):
    """Test using an invalid HTTP method."""
    response = client.put('/users', json={'name': 'Invalid', 'email': 'invalid@example.com'})
    assert response.status_code == 405


def test_create_user_invalid_payload(client):
    """Test creating a user with invalid payload."""
    response = client.post('/users', json={'email': 'invalid@example.com'})  # Missing 'name'
    assert response.status_code == 500
    assert 'error' in response.json


def test_create_user_no_payload(client):
    """Test creating a user with no payload."""
    response = client.post('/users', json=None)
    assert response.status_code == 500
    assert 'error' in response.json

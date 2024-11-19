import pytest
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError
import re


class TestUserModel:

    def test_create_user(self, app, add_user):
        """Test creating a user and saving to the database."""
        with app.app_context():
            """Test creating a user and saving to the database."""
            user = add_user(name="John Doe", email="john@example.com")

            assert user.name == "John Doe"
            assert user.email == "john@example.com"
            assert user.id is not None

            user_from_db = db.session.get(User, user.id)
            assert user_from_db is not None
            assert user_from_db.name == "John Doe"
            assert user_from_db.email == "john@example.com"

    def test_read_user(self, app, add_user):
        """Test retrieving a user from the database."""
        with app.app_context():
        
            user = add_user(name="Jane Doe", email="jane@example.com")

            user_from_db = db.session.get(User, user.id)
            assert user_from_db is not None
            assert user_from_db.name == "Jane Doe"
            assert user_from_db.email == "jane@example.com"

    def test_update_user(self, app, add_user):
        """Test updating an existing user in the database."""
        with app.app_context():
            user = add_user(name="Alice", email="alicetest@example.com")

            # Update the user's name
            user.name = "Alicia"
            db.session.commit()

            # Retrieve the updated user
            updated_user = db.session.get(User, user.id)
            assert updated_user.name == "Alicia"
            assert updated_user.email == "alicetest@example.com"

    def test_delete_user(self, app, add_user):
        """Test deleting a user from the database."""
        with app.app_context():
            user = add_user(name="Bob1", email="bob1@example.com")

            # Ensure the user exists in the database before deletion
            user_from_db = db.session.get(User, user.id)
            assert user_from_db is not None

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            # Ensure the user has been deleted
            deleted_user = db.session.get(User, user.id)
            assert deleted_user is None

    def test_user_email_uniqueness(self, app, add_user):
        """Test that the email field is unique."""
        with app.app_context():
            # Add a user with a specific email
            add_user(name="Charlie1", email="charlie1@example.com")

            # Try to add another user with the same email and catch the exception
            with pytest.raises(IntegrityError):
                add_user(name="Dan", email="charlie1@example.com")

            # Verify that only one user with this email exists
            users_with_same_email = User.query.filter_by(email="charlie1@example.com").all()
            assert len(users_with_same_email) == 1

    def test_user_email_required(self, app, add_user):
        """Test that the email field is required."""
        with app.app_context():
            with pytest.raises(IntegrityError):
                add_user(name="No Email", email='')


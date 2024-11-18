def test_create_user(client):
    """Test creating a user in the test database."""
    response = client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User created'

def test_get_users(client, add_user):
    """Test retrieving users from the test database."""
    add_user("Bob", "bob@example.com")
    response = client.get('/users')
    users = response.get_json()
    assert len(users) == 1
    assert users[0]['name'] == "Bob"
    assert users[0]['email'] == "bob@example.com"

def test_duplicate_user_email(client, add_user):
    """Test handling duplicate emails during user creation."""
    add_user("Charlie", "charlie@example.com")
    response = client.post('/users', json={'name': 'Duplicate Charlie', 'email': 'charlie@example.com'})
    assert response.status_code == 400
    assert "already exists" in response.get_json()['message']

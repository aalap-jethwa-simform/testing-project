import requests
import subprocess
import requests
import time

BASE_URL = "http://127.0.0.1:5000"


def test_e2e_create_and_get_users(client):
    """Test creating and retrieving users."""
    # Create a user
    create_resp = client.post('/users', json={'name': 'Diana', 'email': 'diana@example.com'})
    assert create_resp.status_code == 201
    assert create_resp.get_json()['message'] == 'User created'

    # Retrieve the users
    get_resp = client.get('/users/list')
    users = get_resp.get_json()
    assert len(users) == 1
    assert users[0]['name'] == 'Diana'
    assert users[0]['email'] == 'diana@example.com'


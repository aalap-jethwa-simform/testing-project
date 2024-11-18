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
    get_resp = client.get('/users')
    users = get_resp.get_json()
    assert len(users) == 1
    assert users[0]['name'] == 'Diana'
    assert users[0]['email'] == 'diana@example.com'



def test_e2e_live_server():
    """Run tests with a live Flask server."""
    process = subprocess.Popen(["python", "run.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # Wait for the server to start
        time.sleep(5)

        # Create user
        create_resp = requests.post(f"{BASE_URL}/users", json={'name': 'Eve', 'email': 'eve@example.com'})
        print(f"Create Response: {create_resp.status_code}, {create_resp.json()}")  # Log response
        assert create_resp.status_code == 201

        # Retrieve users
        get_resp = requests.get(f"{BASE_URL}/users")
        users = get_resp.json()
        print(f"Get Response: {get_resp.status_code}, {users}")  # Log response
        assert len(users) == 1
        assert users[0]['name'] == 'Eve'
    finally:
        process.terminate()
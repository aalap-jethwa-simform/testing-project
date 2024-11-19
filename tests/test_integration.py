# from app import db
# from app.models import User


# def test_get_users_empty(client):
#     """Test retrieving users when there are none."""
#     User.query.delete()
#     db.session.commit()
#     response = client.get('/users')
#     users = response.get_json()
#     assert len(users) == 2
#     assert users[1]['name'] == "Bob"
#     assert users[1]['email'] == "bob@example.com"


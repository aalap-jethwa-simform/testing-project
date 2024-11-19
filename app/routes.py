from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from .models import db, User, Project
from helper.constants import INTERNAL_SERVER_ERROR, USER_NOT_FOUND

main = Blueprint('main', __name__)

users = []
projects = []


def find_user_by_id(user_id):
    return next((user for user in users if user['id'] == user_id), None)


def find_project_by_id(project_id):
    return next((project for project in projects if project['id'] == project_id), None)


@main.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask App'})


@main.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Missing name or email'}), 400

        user = User(name=data['name'], email=data['email'])

        db.session.add(user)
        db.session.commit()

        return jsonify({"id": user.id, "message": 'User created'}), 201
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid lingering locks
        if "UNIQUE constraint failed" in str(e):
            return jsonify({'message': 'User with this email already exists'}), 400
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return jsonify({'error': INTERNAL_SERVER_ERROR}), 500


@main.route('/users/list', methods=['GET'])
def get_users_list():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])


# @main.route('v2/users', methods=['GET'])
# def get_users():
#     try:
#         users = User.query.all()
#         user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
#         return jsonify(user_list), 200
#     except Exception:
#         # Catch any exception and return a 500 error
#         return jsonify({'error': 'Internal Server Error'}), 500

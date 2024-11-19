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


@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])


@main.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)
    except Exception as _:
        return jsonify({'message': USER_NOT_FOUND}), 404

    updated_data = request.json
    user.name = updated_data.get("name", user.name)

    try:
        db.session.commit()
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {e}")
        return jsonify({'message': 'Error updating user'}), 500


@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
    except Exception as _:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


@main.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': USER_NOT_FOUND}), 404  # Unauthorized user

        project = Project(name=data['name'], description=data['description'], user_id=user_id)
        db.session.add(project)
        db.session.commit()

        return jsonify({'message': 'Project created', 'project_id': project.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error creating project: {e}")
        return jsonify({'error': INTERNAL_SERVER_ERROR}), 500


@main.route('/projects/<int:user_id>', methods=['GET'])
def get_projects_by_user(user_id):
    try:
        current_user_id = request.args.get('current_user_id')
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403  # Unauthorized access

        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({'error': USER_NOT_FOUND}), 403

        if str(current_user_id) != str(user_id):
            return jsonify({'error': 'Forbidden: You can only access your projects'}), 403

        projects_data = Project.query.filter_by(user_id=user_id).all()
        return jsonify([{'id': p.id, 'name': p.name, 'description': p.description} for p in projects_data]), 200

    except Exception as _:
        return jsonify({'error': INTERNAL_SERVER_ERROR}), 500


@main.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project by ID."""
    try:
        project = Project.query.get(project_id)
    except Exception as _:
        return jsonify({'message': 'Project not found'}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200

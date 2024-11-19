from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from .models import db, User

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask App'})

@main.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user = User(name=data['name'], email=data['email'])

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created'}), 201
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid lingering locks
        if "duplicate key value violates unique constraint" in str(e):
            return jsonify({'message': 'User with this email already exists'}), 400
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])


@main.route('v2/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return jsonify(user_list), 200
    except Exception:
        # Catch any exception and return a 500 error
        return jsonify({'error': 'Internal Server Error'}), 500
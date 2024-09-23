from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
# from flask_jwt_extended import create_access_token, create_refresh_token
from .models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Check if both fields are provided
    if not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing username or password"}), 400

    # Find the user in the database
    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if the password matches
    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid password"}), 401

    # If credentials are correct, create tokens (JWT)
    # access_token = create_access_token(identity=user.public_id)
    # refresh_token = create_refresh_token(identity=user.public_id)

    return jsonify({
        "message": "Login successful",
        # "access_token": access_token,
        # "refresh_token": refresh_token
    }), 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Basic validation
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400

    # Password hashing
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201
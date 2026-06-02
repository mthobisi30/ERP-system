"""Authentication Routes."""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt,
)
from flask_bcrypt import generate_password_hash, check_password_hash

from config.database import db
from app.models.user import User
from app.models.auth import TokenBlocklist
from app.services.email_service import EmailService
from app.extensions import limiter

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    data = request.get_json() or {}
    for field in ('email', 'username', 'password'):
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Self-registration never grants elevated roles.
    user = User(
        email=data['email'],
        username=data['username'],
        password_hash=generate_password_hash(data['password']).decode('utf-8'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role='employee',
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create user', 'detail': str(exc)}), 400

    try:
        EmailService.send_welcome_email(user.email, user.username)
    except Exception:  # noqa: BLE001 — email failure must not break registration
        pass

    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not check_password_hash(user.password_hash, data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'access_token': create_access_token(identity=str(user.id)),
        'refresh_token': create_refresh_token(identity=str(user.id)),
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    return jsonify({'access_token': create_access_token(identity=identity)}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = db.session.get(User, get_jwt_identity())
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json() or {}
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'current_password and new_password are required'}), 400
    user = db.session.get(User, get_jwt_identity())
    if user is None or not check_password_hash(user.password_hash, data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    if len(data['new_password']) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    user.password_hash = generate_password_hash(data['new_password']).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Password updated'}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
def logout():
    """Revoke the presented token by recording its jti in the blocklist."""
    token = get_jwt()
    db.session.add(TokenBlocklist(jti=token['jti'], user_id=get_jwt_identity()))
    db.session.commit()
    return jsonify({'message': 'Logged out successfully'}), 200

"""User Management Routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import generate_password_hash

from config.database import db
from app.models.user import User
from app.utils.decorators import min_role, admin_required, get_current_user

users_bp = Blueprint('users', __name__)

# Fields a normal user may never set on themselves; only admins may.
PRIVILEGED_FIELDS = {'role', 'is_active'}
# Fields nobody may set through this endpoint.
PROTECTED_FIELDS = {'id', 'password_hash', 'created_at', 'updated_at'}


@users_bp.route('', methods=['GET'])
@min_role('manager')
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    users = User.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    }), 200


@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """Admin-provisioned user (with role + password)."""
    data = request.get_json() or {}
    for field in ('email', 'username', 'password'):
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    role = data.get('role', 'employee')
    if role not in ('employee', 'manager', 'admin'):
        return jsonify({'error': 'Invalid role'}), 400
    user = User(
        email=data['email'],
        username=data['username'],
        password_hash=generate_password_hash(data['password']).decode('utf-8'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=role,
        position=data.get('position'),
        is_active=True,
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create user', 'detail': str(exc)}), 400
    return jsonify(user.to_dict()), 201


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    actor = get_current_user()
    if actor is None:
        return jsonify({'error': 'Unauthorized'}), 401
    # A user may edit themselves; otherwise admin only.
    is_admin = actor.role == 'admin'
    if str(actor.id) != str(user_id) and not is_admin:
        return jsonify({'error': 'Forbidden', 'message': 'You can only edit your own profile'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    for key, value in data.items():
        if key in PROTECTED_FIELDS:
            continue
        if key in PRIVILEGED_FIELDS and not is_admin:
            continue  # silently ignore privilege-escalation attempts
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update user', 'detail': str(exc)}), 400
    return jsonify(user.to_dict()), 200


@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if str(get_jwt_identity()) == str(user_id):
        return jsonify({'error': 'You cannot delete your own account'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

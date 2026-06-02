"""Authorization decorators.

Authorization is based on ``User.role`` with a simple hierarchy:
    employee (1) < manager (2) < admin (3)

Note: ``User.role`` is the *authorization* role. A person's job title /
seniority band (used for rate-card matching) lives in ``User.position``.
"""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from config.database import db
from app.models.user import User

ROLE_LEVELS = {'employee': 1, 'manager': 2, 'admin': 3}


def get_current_user():
    """Return the authenticated User (or None). Assumes a verified JWT."""
    uid = get_jwt_identity()
    if not uid:
        return None
    return db.session.get(User, uid)


def _authenticated_user_or_error():
    verify_jwt_in_request()
    user = get_current_user()
    if user is None or not user.is_active:
        return None, (jsonify({'error': 'Unauthorized', 'message': 'Invalid or inactive account'}), 401)
    return user, None


def roles_required(*roles):
    """Allow only users whose role is exactly one of ``roles``."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, err = _authenticated_user_or_error()
            if err:
                return err
            if user.role not in roles:
                return jsonify({'error': 'Forbidden',
                                'message': f'Requires role: {", ".join(roles)}'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def min_role(role):
    """Allow users at ``role`` level or above (employee < manager < admin)."""
    threshold = ROLE_LEVELS.get(role, 99)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, err = _authenticated_user_or_error()
            if err:
                return err
            if ROLE_LEVELS.get(user.role, 0) < threshold:
                return jsonify({'error': 'Forbidden',
                                'message': f'Requires {role} access or higher'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    return roles_required('admin')(fn)

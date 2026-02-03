"""Authentication Middleware"""
from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
    return decorated_function

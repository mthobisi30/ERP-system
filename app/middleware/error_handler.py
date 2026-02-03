"""Error Handlers"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

def handle_http_exception(error):
    """Handle HTTP exceptions"""
    response = {
        'error': error.name,
        'message': error.description,
        'status_code': error.code
    }
    return jsonify(response), error.code

def handle_generic_exception(error):
    """Handle generic exceptions"""
    response = {
        'error': 'Internal Server Error',
        'message': str(error),
        'status_code': 500
    }
    return jsonify(response), 500

def register_error_handlers(app):
    """Register all error handlers with app"""
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_generic_exception)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.settings import CompanySettings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('', methods=['GET'])
@jwt_required()
def get_settings():
    settings = CompanySettings.query.first()
    if not settings:
        return jsonify({'message': 'No settings found'}), 404
    return jsonify({'company_name': settings.company_name, 'email': settings.email, 'currency': settings.currency}), 200

@settings_bp.route('', methods=['PUT'])
@jwt_required()
def update_settings():
    settings = CompanySettings.query.first()
    if not settings:
        settings = CompanySettings()
        db.session.add(settings)
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    db.session.commit()
    return jsonify({'message': 'Settings updated'}), 200

@settings_bp.route('/system-status', methods=['GET'])
@jwt_required()
def get_system_status():
    """Returns the configuration status for external services."""
    from flask import current_app
    
    config = current_app.config
    
    # Check what services are configured
    storage_provider = 'Cloudinary' if config.get('CLOUDINARY_URL') or config.get('CLOUDINARY_API_KEY') else \
                       'AWS S3' if config.get('AWS_ACCESS_KEY_ID') else 'Local'
    
    smtp_configured = bool(config.get('MAIL_USERNAME') and config.get('MAIL_PASSWORD'))
    stripe_configured = bool(config.get('STRIPE_SECRET_KEY'))
    
    return jsonify({
        'storage': {
            'provider': storage_provider,
            'configured': storage_provider != 'Local'
        },
        'email': {
            'smtp_configured': smtp_configured,
            'server': config.get('MAIL_SERVER'),
            'sender': config.get('MAIL_DEFAULT_SENDER')
        },
        'payments': {
            'stripe_configured': stripe_configured
        },
        'company': {
            'name': config.get('COMPANY_NAME'),
            'email': config.get('COMPANY_EMAIL'),
            'currency': config.get('DEFAULT_CURRENCY'),
            'timezone': config.get('TIMEZONE')
        }
    }), 200

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

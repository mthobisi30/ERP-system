"""Module enable/disable configuration."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.module import ModuleConfig
from app.utils.decorators import admin_required

modules_bp = Blueprint('modules', __name__)


@modules_bp.route('', methods=['GET'])
@jwt_required()
def list_modules():
    ModuleConfig.ensure_seeded()
    mods = ModuleConfig.query.order_by(ModuleConfig.category.asc(), ModuleConfig.label.asc()).all()
    return jsonify({
        'modules': [m.to_dict() for m in mods],
        'enabled': [m.key for m in mods if m.enabled],
    }), 200


@modules_bp.route('/enabled', methods=['GET'])
@jwt_required()
def enabled_modules():
    """Lightweight list of enabled module keys — used to gate the sidebar nav."""
    ModuleConfig.ensure_seeded()
    mods = ModuleConfig.query.all()
    return jsonify({
        'enabled': [m.key for m in mods if m.enabled],
        'all': [m.key for m in mods],
    }), 200


@modules_bp.route('/<key>', methods=['PUT'])
@admin_required
def toggle_module(key):
    module = ModuleConfig.query.filter_by(key=key).first_or_404()
    if module.is_core:
        return jsonify({'error': 'Core modules cannot be disabled'}), 400
    data = request.get_json() or {}
    module.enabled = bool(data.get('enabled', not module.enabled))
    db.session.commit()
    return jsonify(module.to_dict()), 200

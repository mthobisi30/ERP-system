from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.log import ActivityLog, SystemLog

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50)
    return jsonify({
        'logs': [{'id': str(l.id), 'action': l.action, 'entity_type': l.entity_type, 'created_at': l.created_at.isoformat()} for l in logs.items],
        'total': logs.total
    }), 200

@logs_bp.route('/system', methods=['GET'])
@jwt_required()
def get_system_logs():
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(100).all()
    return jsonify([{'id': str(l.id), 'level': l.log_level, 'message': l.message, 'created_at': l.created_at.isoformat()} for l in logs]), 200

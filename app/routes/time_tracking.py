from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.schedule import TimeEntry

time_tracking_bp = Blueprint('time_tracking', __name__)

@time_tracking_bp.route('', methods=['GET'])
@jwt_required()
def get_time_entries():
    user_id = get_jwt_identity()
    entries = TimeEntry.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': str(e.id), 'description': e.description, 'duration': e.duration_minutes} for e in entries]), 200

@time_tracking_bp.route('', methods=['POST'])
@jwt_required()
def create_time_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    data['user_id'] = user_id
    entry = TimeEntry(**data)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': str(entry.id), 'message': 'Time entry created'}), 201

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.schedule import Schedule

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('', methods=['GET'])
@jwt_required()
def get_schedules():
    user_id = get_jwt_identity()
    schedules = Schedule.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': str(s.id), 'title': s.title, 'start': s.start_time.isoformat(), 'end': s.end_time.isoformat()} for s in schedules]), 200

@schedule_bp.route('', methods=['POST'])
@jwt_required()
def create_schedule():
    user_id = get_jwt_identity()
    data = request.get_json()
    data['user_id'] = user_id
    schedule = Schedule(**data)
    db.session.add(schedule)
    db.session.commit()
    return jsonify({'id': str(schedule.id), 'message': 'Schedule created'}), 201

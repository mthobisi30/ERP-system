from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.hr import PerformanceReview, Attendance, Leave

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/performance-reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    reviews = PerformanceReview.query.all()
    return jsonify([{'id': str(r.id), 'employee_id': str(r.employee_id), 'status': r.status} for r in reviews]), 200

@hr_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    records = Attendance.query.all()
    return jsonify([{'id': str(a.id), 'user_id': str(a.user_id), 'date': a.attendance_date.isoformat(), 'status': a.status} for a in records]), 200

@hr_bp.route('/leaves', methods=['GET'])
@jwt_required()
def get_leaves():
    leaves = Leave.query.all()
    return jsonify([{'id': str(l.id), 'user_id': str(l.user_id), 'type': l.leave_type, 'status': l.status} for l in leaves]), 200

@hr_bp.route('/leaves', methods=['POST'])
@jwt_required()
def create_leave():
    data = request.get_json()
    leave = Leave(**data)
    db.session.add(leave)
    db.session.commit()
    return jsonify({'id': str(leave.id), 'message': 'Leave request created'}), 201

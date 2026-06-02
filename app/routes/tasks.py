"""Task Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.task import Task, TaskComment

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Task.query
    for field in ('status', 'assigned_to', 'project_id', 'sprint_id'):
        if request.args.get(field):
            query = query.filter(getattr(Task, field) == request.args.get(field))

    tasks = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'tasks': [t.to_dict() for t in tasks.items],
        'total': tasks.total
    }), 200

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    data['created_by'] = user_id
    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.session.commit()
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200

@tasks_bp.route('/<task_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(task_id):
    comments = TaskComment.query.filter_by(task_id=task_id).all()
    return jsonify([{'id': str(c.id), 'comment': c.comment, 'created_at': c.created_at.isoformat()} for c in comments]), 200

@tasks_bp.route('/<task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    comment = TaskComment(task_id=task_id, user_id=user_id, comment=data['comment'])
    db.session.add(comment)
    db.session.commit()
    return jsonify({'message': 'Comment added'}), 201

"""Project Management Routes"""
from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.project import Project, Sprint, Milestone
from app.models.schedule import TimeEntry

projects_bp = Blueprint('projects', __name__)


def _parse_date(value, default=None):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Project.query
    if status:
        query = query.filter_by(status=status)
    
    projects = query.paginate(page=page, per_page=per_page)
    return jsonify({
        'projects': [p.to_dict() for p in projects.items],
        'total': projects.total
    }), 200

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json()
    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict()), 200

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(project, key):
            setattr(project, key, value)
    db.session.commit()
    return jsonify(project.to_dict()), 200

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200

@projects_bp.route('/<project_id>/milestones', methods=['GET'])
@jwt_required()
def get_milestones(project_id):
    milestones = Milestone.query.filter_by(project_id=project_id).all()
    return jsonify([m.to_dict() for m in milestones]), 200

@projects_bp.route('/<project_id>/milestones', methods=['POST'])
@jwt_required()
def create_milestone(project_id):
    data = request.get_json()
    data['project_id'] = project_id
    milestone = Milestone(**data)
    db.session.add(milestone)
    db.session.commit()
    return jsonify(milestone.to_dict()), 201

# ---- Sprints ----

@projects_bp.route('/<project_id>/sprints', methods=['GET'])
@jwt_required()
def get_sprints(project_id):
    sprints = Sprint.query.filter_by(project_id=project_id).order_by(Sprint.start_date.asc()).all()
    return jsonify({'sprints': [s.to_dict() for s in sprints]}), 200

@projects_bp.route('/<project_id>/sprints', methods=['POST'])
@jwt_required()
def create_sprint(project_id):
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    sprint = Sprint(
        project_id=project_id,
        name=data['name'],
        goal=data.get('goal'),
        status=data.get('status', 'planned'),
        start_date=_parse_date(data.get('start_date')),
        end_date=_parse_date(data.get('end_date')),
    )
    db.session.add(sprint)
    db.session.commit()
    return jsonify(sprint.to_dict()), 201

@projects_bp.route('/sprints/<sprint_id>', methods=['PUT'])
@jwt_required()
def update_sprint(sprint_id):
    sprint = Sprint.query.get_or_404(sprint_id)
    data = request.get_json() or {}
    for key in ('name', 'goal', 'status'):
        if key in data:
            setattr(sprint, key, data[key])
    if 'start_date' in data:
        sprint.start_date = _parse_date(data['start_date'], sprint.start_date)
    if 'end_date' in data:
        sprint.end_date = _parse_date(data['end_date'], sprint.end_date)
    db.session.commit()
    return jsonify(sprint.to_dict()), 200

# ---- Billing summary ----

@projects_bp.route('/<project_id>/unbilled-time', methods=['GET'])
@jwt_required()
def unbilled_time(project_id):
    """Summary of unbilled billable time for the project (drives invoicing)."""
    entries = (TimeEntry.query
               .filter(TimeEntry.project_id == project_id,
                       TimeEntry.billable.is_(True),
                       TimeEntry.invoiced.is_(False),
                       TimeEntry.hours > 0)
               .order_by(TimeEntry.entry_date.asc())
               .all())
    return jsonify({
        'project_id': project_id,
        'entry_count': len(entries),
        'total_hours': sum(float(e.hours or 0) for e in entries),
        'total_amount': sum(e.amount for e in entries),
        'entries': [e.to_dict() for e in entries],
    }), 200

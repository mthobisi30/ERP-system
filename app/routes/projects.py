"""Project Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.project import Project, Milestone

projects_bp = Blueprint('projects', __name__)

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

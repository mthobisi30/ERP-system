"""Opportunity Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.customer import Opportunity
from app.models.project import Project
from app.services.activity import record

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('', methods=['GET'])
@jwt_required()
def get_opportunities():
    page = request.args.get('page', 1, type=int)
    opportunities = Opportunity.query.paginate(page=page, per_page=20)
    return jsonify({'opportunities': [o.to_dict() for o in opportunities.items]}), 200

@opportunities_bp.route('', methods=['POST'])
@jwt_required()
def create_opportunity():
    data = request.get_json()
    opp = Opportunity(**data)
    db.session.add(opp)
    db.session.commit()
    return jsonify(opp.to_dict()), 201

@opportunities_bp.route('/<opp_id>', methods=['GET'])
@jwt_required()
def get_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    return jsonify(opp.to_dict()), 200

@opportunities_bp.route('/<opp_id>', methods=['PUT'])
@jwt_required()
def update_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(opp, key):
            setattr(opp, key, value)
    db.session.commit()
    return jsonify(opp.to_dict()), 200

@opportunities_bp.route('/<opp_id>', methods=['DELETE'])
@jwt_required()
def delete_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted'}), 200

@opportunities_bp.route('/<opp_id>/convert-to-project', methods=['POST'])
@jwt_required()
def convert_to_project(opp_id):
    """Win an opportunity: create a Project from it and mark it closed_won."""
    opp = Opportunity.query.get_or_404(opp_id)
    data = request.get_json() or {}
    project = Project(
        name=data.get('name') or opp.name,
        description=data.get('description') or opp.description,
        customer_id=opp.customer_id,
        opportunity_id=opp.id,
        status='active',
        billing_type=data.get('billing_type', 'time_and_materials'),
        billing_rate=data.get('billing_rate'),
        budget=data.get('budget') if data.get('budget') is not None else opp.estimated_value,
        currency=data.get('currency', 'ZAR'),
    )
    opp.stage = 'closed_won'
    opp.status = 'won'
    try:
        db.session.add(project)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not convert opportunity', 'detail': str(exc)}), 400
    record('opportunity.converted', 'project', project.id, project_id=project.id,
           customer_id=project.customer_id, summary=f"Opportunity '{opp.name}' converted → project {project.name}")
    return jsonify({'message': 'Opportunity converted to project', 'project': project.to_dict()}), 201

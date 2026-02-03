"""Lead Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.customer import Lead

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('', methods=['GET'])
@jwt_required()
def get_leads():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    query = Lead.query
    if status:
        query = query.filter_by(status=status)
    leads = query.paginate(page=page, per_page=per_page)
    return jsonify({'leads': [l.to_dict() for l in leads.items], 'total': leads.total}), 200

@leads_bp.route('', methods=['POST'])
@jwt_required()
def create_lead():
    data = request.get_json()
    lead = Lead(**data)
    db.session.add(lead)
    db.session.commit()
    return jsonify(lead.to_dict()), 201

@leads_bp.route('/<lead_id>', methods=['GET'])
@jwt_required()
def get_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    return jsonify(lead.to_dict()), 200

@leads_bp.route('/<lead_id>', methods=['PUT'])
@jwt_required()
def update_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(lead, key):
            setattr(lead, key, value)
    db.session.commit()
    return jsonify(lead.to_dict()), 200

@leads_bp.route('/<lead_id>', methods=['DELETE'])
@jwt_required()
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({'message': 'Lead deleted'}), 200

"""Opportunity Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.customer import Opportunity

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

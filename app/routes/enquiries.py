"""Enquiry management routes (internal view of website enquiries)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.enquiry import Enquiry

enquiries_bp = Blueprint('enquiries', __name__)


@enquiries_bp.route('', methods=['GET'])
@jwt_required()
def list_enquiries():
    q = Enquiry.query
    if request.args.get('status'):
        q = q.filter_by(status=request.args.get('status'))
    items = q.order_by(Enquiry.created_at.desc()).all()
    return jsonify({
        'enquiries': [e.to_dict() for e in items],
        'total': len(items),
        'new_count': sum(1 for e in items if e.status == 'new'),
    }), 200


@enquiries_bp.route('/<enquiry_id>', methods=['GET'])
@jwt_required()
def get_enquiry(enquiry_id):
    return jsonify(Enquiry.query.get_or_404(enquiry_id).to_dict()), 200


@enquiries_bp.route('/<enquiry_id>', methods=['PUT'])
@jwt_required()
def update_enquiry(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    data = request.get_json() or {}
    if data.get('status') in ('new', 'read', 'responded', 'archived'):
        enquiry.status = data['status']
    db.session.commit()
    return jsonify(enquiry.to_dict()), 200


@enquiries_bp.route('/<enquiry_id>', methods=['DELETE'])
@jwt_required()
def delete_enquiry(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    db.session.delete(enquiry)
    db.session.commit()
    return jsonify({'message': 'Enquiry deleted'}), 200

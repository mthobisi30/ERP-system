from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.accounting import Invoice

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    page = request.args.get('page', 1, type=int)
    invoices = Invoice.query.paginate(page=page, per_page=20)
    return jsonify({'invoices': [i.to_dict() for i in invoices.items], 'total': invoices.total}), 200

@invoices_bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    data = request.get_json()
    invoice = Invoice(**data)
    db.session.add(invoice)
    db.session.commit()
    return jsonify(invoice.to_dict()), 201

@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(invoice.to_dict()), 200

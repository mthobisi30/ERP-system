from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.purchase import Supplier

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([s.to_dict() for s in suppliers]), 200

@suppliers_bp.route('', methods=['POST'])
@jwt_required()
def create_supplier():
    data = request.get_json()
    supplier = Supplier(**data)
    db.session.add(supplier)
    db.session.commit()
    return jsonify(supplier.to_dict()), 201

@suppliers_bp.route('/<supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify(supplier.to_dict()), 200

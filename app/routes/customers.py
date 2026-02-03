"""Customer Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.customer import Customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    customers = Customer.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'customers': [c.to_dict() for c in customers.items],
        'total': customers.total
    }), 200

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json()
    customer = Customer(**data)
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201

@customers_bp.route('/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/<customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    db.session.commit()
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/<customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'}), 200

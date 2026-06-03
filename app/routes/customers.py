"""Customer Management Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.customer import Customer
from app.utils.codes import next_customer_code

customers_bp = Blueprint('customers', __name__)

_CUST_FIELDS = {'customer_code', 'company_name', 'contact_person', 'email', 'phone', 'mobile',
                'website', 'industry', 'customer_type', 'status', 'billing_address',
                'shipping_address', 'tax_id', 'payment_terms', 'credit_limit'}

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
    data = request.get_json() or {}
    if not data.get('company_name') and not data.get('contact_person'):
        return jsonify({'error': 'company_name (or contact_person) is required'}), 400
    customer = Customer(**{k: v for k, v in data.items() if k in _CUST_FIELDS})
    if not customer.customer_code:
        customer.customer_code = next_customer_code(customer.company_name or customer.contact_person)
    try:
        db.session.add(customer)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create customer', 'detail': str(exc)}), 400
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

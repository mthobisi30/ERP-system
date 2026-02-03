from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.sales import SalesOrder, Quotation

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_sales_orders():
    page = request.args.get('page', 1, type=int)
    orders = SalesOrder.query.paginate(page=page, per_page=20)
    return jsonify({'orders': [o.to_dict() for o in orders.items], 'total': orders.total}), 200

@sales_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_sales_order():
    data = request.get_json()
    order = SalesOrder(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201

@sales_bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_sales_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200

@sales_bp.route('/quotations', methods=['GET'])
@jwt_required()
def get_quotations():
    quotations = Quotation.query.paginate(page=1, per_page=20)
    return jsonify({'quotations': [q.to_dict() for q in quotations.items]}), 200

@sales_bp.route('/quotations', methods=['POST'])
@jwt_required()
def create_quotation():
    data = request.get_json()
    quote = Quotation(**data)
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201

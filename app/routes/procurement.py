from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.purchase import PurchaseOrder

procurement_bp = Blueprint('procurement', __name__)

@procurement_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
def get_purchase_orders():
    page = request.args.get('page', 1, type=int)
    orders = PurchaseOrder.query.paginate(page=page, per_page=20)
    return jsonify({'orders': [o.to_dict() for o in orders.items], 'total': orders.total}), 200

@procurement_bp.route('/purchase-orders', methods=['POST'])
@jwt_required()
def create_purchase_order():
    data = request.get_json()
    order = PurchaseOrder(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201

@procurement_bp.route('/purchase-orders/<order_id>', methods=['GET'])
@jwt_required()
def get_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200

@procurement_bp.route('/purchase-orders/<order_id>', methods=['PUT'])
@jwt_required()
def update_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(order, key):
            setattr(order, key, value)
    db.session.commit()
    return jsonify(order.to_dict()), 200

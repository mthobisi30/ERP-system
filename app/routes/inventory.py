from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.inventory import Inventory, Warehouse

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('', methods=['GET'])
@jwt_required()
def get_inventory():
    items = Inventory.query.all()
    return jsonify([{'product_id': str(i.product_id), 'warehouse_id': str(i.warehouse_id), 'quantity': float(i.quantity_on_hand)} for i in items]), 200

@inventory_bp.route('/warehouses', methods=['GET'])
@jwt_required()
def get_warehouses():
    warehouses = Warehouse.query.all()
    return jsonify([w.to_dict() for w in warehouses]), 200

@inventory_bp.route('/warehouses', methods=['POST'])
@jwt_required()
def create_warehouse():
    data = request.get_json()
    warehouse = Warehouse(**data)
    db.session.add(warehouse)
    db.session.commit()
    return jsonify(warehouse.to_dict()), 201

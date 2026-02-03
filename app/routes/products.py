from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.product import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=20)
    return jsonify({'products': [p.to_dict() for p in products.items], 'total': products.total}), 200

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@products_bp.route('/<product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.session.commit()
    return jsonify(product.to_dict()), 200

@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200

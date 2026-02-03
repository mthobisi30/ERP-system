from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.accounting import Payment

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    payments = Payment.query.all()
    return jsonify([{'id': str(p.id), 'number': p.payment_number, 'amount': float(p.amount), 'date': p.payment_date.isoformat()} for p in payments]), 200

@payments_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    payment = Payment(**data)
    db.session.add(payment)
    db.session.commit()
    return jsonify({'id': str(payment.id), 'message': 'Payment recorded'}), 201

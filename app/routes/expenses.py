from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.accounting import Expense

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([{'id': str(e.id), 'number': e.expense_number, 'amount': float(e.amount), 'status': e.status} for e in expenses]), 200

@expenses_bp.route('', methods=['POST'])
@jwt_required()
def create_expense():
    data = request.get_json()
    expense = Expense(**data)
    db.session.add(expense)
    db.session.commit()
    return jsonify({'id': str(expense.id), 'message': 'Expense created'}), 201

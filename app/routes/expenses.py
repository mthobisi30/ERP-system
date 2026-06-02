"""Expense Routes — project-linked, feeds into profitability."""
from datetime import date, datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from config.database import db
from app.models.accounting import Expense
from app.utils.decorators import min_role

expenses_bp = Blueprint('expenses', __name__)

_ALLOWED = {'project_id', 'description', 'category', 'amount', 'billable', 'expense_date'}


def _next_expense_number():
    return f"EXP-{Expense.query.count() + 1:05d}"


@expenses_bp.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    q = Expense.query
    for field in ('project_id', 'status'):
        if request.args.get(field):
            q = q.filter(getattr(Expense, field) == request.args.get(field))
    expenses = q.order_by(Expense.expense_date.desc()).all()
    return jsonify({'expenses': [e.to_dict() for e in expenses], 'total': len(expenses)}), 200


@expenses_bp.route('', methods=['POST'])
@jwt_required()
def create_expense():
    data = request.get_json() or {}
    if data.get('amount') is None:
        return jsonify({'error': 'amount is required'}), 400

    expense = Expense(
        expense_number=data.get('expense_number') or _next_expense_number(),
        created_by=get_jwt_identity(),
        # accept either 'expense_date' or 'date' (the tools form sends 'date')
        expense_date=_parse_date(data.get('expense_date') or data.get('date'), date.today()),
        status='pending',
    )
    for key in _ALLOWED:
        if key in data and key != 'expense_date':
            setattr(expense, key, data[key])
    try:
        db.session.add(expense)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create expense', 'detail': str(exc)}), 400
    return jsonify(expense.to_dict()), 201


@expenses_bp.route('/<expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    return jsonify(Expense.query.get_or_404(expense_id).to_dict()), 200


@expenses_bp.route('/<expense_id>/approve', methods=['POST'])
@min_role('manager')
def approve_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    decision = (request.get_json(silent=True) or {}).get('decision', 'approved')
    expense.status = 'rejected' if decision == 'rejected' else 'approved'
    expense.approved_at = datetime.utcnow()
    db.session.commit()
    return jsonify(expense.to_dict()), 200


@expenses_bp.route('/<expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted'}), 200


def _parse_date(value, default):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default

"""Retainer Contract Routes — recurring monthly billing."""
from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.retainer import RetainerContract
from app.services.billing_service import run_retainers
from app.utils.decorators import min_role

retainers_bp = Blueprint('retainers', __name__)

_ALLOWED = {'name', 'customer_id', 'project_id', 'monthly_fee', 'currency',
            'billing_day', 'vat_applicable', 'status', 'start_date', 'end_date', 'notes'}
_DATE_FIELDS = {'start_date', 'end_date'}


def _apply(contract, data):
    for key, value in data.items():
        if key not in _ALLOWED:
            continue
        if key in _DATE_FIELDS and value:
            try:
                value = date.fromisoformat(value)
            except (ValueError, TypeError):
                continue
        setattr(contract, key, value)


@retainers_bp.route('', methods=['GET'])
@jwt_required()
def get_retainers():
    q = RetainerContract.query
    if request.args.get('status'):
        q = q.filter_by(status=request.args.get('status'))
    if request.args.get('customer_id'):
        q = q.filter_by(customer_id=request.args.get('customer_id'))
    contracts = q.order_by(RetainerContract.name.asc()).all()
    mrr = sum(float(c.monthly_fee or 0) for c in contracts if c.status == 'active')
    return jsonify({'retainers': [c.to_dict() for c in contracts],
                    'total': len(contracts), 'mrr': mrr}), 200


@retainers_bp.route('', methods=['POST'])
@min_role('manager')
def create_retainer():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('customer_id') or data.get('monthly_fee') is None:
        return jsonify({'error': 'name, customer_id and monthly_fee are required'}), 400
    contract = RetainerContract()
    _apply(contract, data)
    try:
        db.session.add(contract)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create retainer', 'detail': str(exc)}), 400
    return jsonify(contract.to_dict()), 201


@retainers_bp.route('/run', methods=['POST'])
@min_role('manager')
def run():
    """Generate this period's retainer invoices (idempotent). Body: {period?: 'YYYY-MM'}."""
    data = request.get_json(silent=True) or {}
    try:
        result = run_retainers(period=data.get('period'))
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not run retainers', 'detail': str(exc)}), 400
    created = result['created']
    return jsonify({
        'period': result['period'],
        'created_count': len(created),
        'skipped_count': result['skipped'],
        'invoices': [inv.to_dict() for inv in created],
    }), 201


@retainers_bp.route('/<retainer_id>', methods=['GET'])
@jwt_required()
def get_retainer(retainer_id):
    return jsonify(RetainerContract.query.get_or_404(retainer_id).to_dict()), 200


@retainers_bp.route('/<retainer_id>', methods=['PUT'])
@min_role('manager')
def update_retainer(retainer_id):
    contract = RetainerContract.query.get_or_404(retainer_id)
    _apply(contract, request.get_json() or {})
    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update retainer', 'detail': str(exc)}), 400
    return jsonify(contract.to_dict()), 200


@retainers_bp.route('/<retainer_id>', methods=['DELETE'])
@min_role('manager')
def delete_retainer(retainer_id):
    contract = RetainerContract.query.get_or_404(retainer_id)
    db.session.delete(contract)
    db.session.commit()
    return jsonify({'message': 'Retainer deleted'}), 200

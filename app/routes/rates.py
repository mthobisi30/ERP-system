"""Rate Card Routes — manage default billing/cost rates."""
from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.rate import RateCard
from app.utils.decorators import min_role

rates_bp = Blueprint('rates', __name__)

_ALLOWED = {'name', 'role', 'user_id', 'bill_rate', 'cost_rate',
            'currency', 'unit', 'is_active', 'effective_date'}


def _apply(rate, data):
    for key, value in data.items():
        if key not in _ALLOWED:
            continue
        if key == 'effective_date' and value:
            try:
                value = date.fromisoformat(value)
            except (ValueError, TypeError):
                continue
        setattr(rate, key, value)


@rates_bp.route('', methods=['GET'])
@jwt_required()
def get_rate_cards():
    q = RateCard.query
    if request.args.get('active') == 'true':
        q = q.filter(RateCard.is_active.is_(True))
    rates = q.order_by(RateCard.name.asc()).all()
    return jsonify({'rate_cards': [r.to_dict() for r in rates], 'total': len(rates)}), 200


@rates_bp.route('', methods=['POST'])
@min_role('manager')
def create_rate_card():
    data = request.get_json() or {}
    if not data.get('name') or data.get('bill_rate') is None:
        return jsonify({'error': 'name and bill_rate are required'}), 400
    rate = RateCard()
    _apply(rate, data)
    try:
        db.session.add(rate)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create rate card', 'detail': str(exc)}), 400
    return jsonify(rate.to_dict()), 201


@rates_bp.route('/<rate_id>', methods=['GET'])
@jwt_required()
def get_rate_card(rate_id):
    return jsonify(RateCard.query.get_or_404(rate_id).to_dict()), 200


@rates_bp.route('/<rate_id>', methods=['PUT'])
@min_role('manager')
def update_rate_card(rate_id):
    rate = RateCard.query.get_or_404(rate_id)
    _apply(rate, request.get_json() or {})
    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update rate card', 'detail': str(exc)}), 400
    return jsonify(rate.to_dict()), 200


@rates_bp.route('/<rate_id>', methods=['DELETE'])
@min_role('manager')
def delete_rate_card(rate_id):
    rate = RateCard.query.get_or_404(rate_id)
    db.session.delete(rate)
    db.session.commit()
    return jsonify({'message': 'Rate card deleted'}), 200

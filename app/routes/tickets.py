"""Support Ticket Routes — linked to client + project."""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.ticket import Ticket, TicketResponse
from app.services.activity import record

tickets_bp = Blueprint('tickets', __name__)

_FIELDS = {'customer_id', 'project_id', 'subject', 'description', 'priority',
           'status', 'category', 'assigned_to'}


def _next_ticket_number():
    return f"TKT-{Ticket.query.count() + 1:05d}"


@tickets_bp.route('', methods=['GET'])
@jwt_required()
def get_tickets():
    q = Ticket.query
    for field in ('customer_id', 'project_id', 'status', 'priority'):
        if request.args.get(field):
            q = q.filter(getattr(Ticket, field) == request.args.get(field))
    tickets = q.order_by(Ticket.created_at.desc()).all()
    return jsonify({
        'tickets': [t.to_dict() for t in tickets],
        'total': len(tickets),
        'open_count': sum(1 for t in tickets if t.status not in ('resolved', 'closed')),
    }), 200


@tickets_bp.route('', methods=['POST'])
@jwt_required()
def create_ticket():
    data = request.get_json() or {}
    if not data.get('subject'):
        return jsonify({'error': 'subject is required'}), 400
    ticket = Ticket(ticket_number=data.get('ticket_number') or _next_ticket_number())
    for k in _FIELDS:
        if k in data:
            setattr(ticket, k, data[k] or None if k.endswith('_id') else data[k])
    if data.get('due_date'):
        try:
            ticket.due_date = datetime.fromisoformat(data['due_date'])
        except (ValueError, TypeError):
            pass
    try:
        db.session.add(ticket)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create ticket', 'detail': str(exc)}), 400
    record('ticket.created', 'ticket', ticket.id, project_id=ticket.project_id,
           customer_id=ticket.customer_id, summary=f"Ticket {ticket.ticket_number} opened: {ticket.subject}")
    return jsonify(ticket.to_dict()), 201


@tickets_bp.route('/<ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    payload = ticket.to_dict()
    payload['responses'] = [{'id': str(r.id), 'response': r.response, 'is_internal': r.is_internal,
                             'created_at': r.created_at.isoformat() if r.created_at else None}
                            for r in TicketResponse.query.filter_by(ticket_id=ticket.id).all()]
    return jsonify(payload), 200


@tickets_bp.route('/<ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    for k in _FIELDS:
        if k in data:
            setattr(ticket, k, data[k])
    db.session.commit()
    return jsonify(ticket.to_dict()), 200


@tickets_bp.route('/<ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    TicketResponse.query.filter_by(ticket_id=ticket.id).delete()
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted'}), 200

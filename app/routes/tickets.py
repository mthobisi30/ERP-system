from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.ticket import Ticket

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('', methods=['GET'])
@jwt_required()
def get_tickets():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.paginate(page=page, per_page=20)
    return jsonify({'tickets': [t.to_dict() for t in tickets.items], 'total': tickets.total}), 200

@tickets_bp.route('', methods=['POST'])
@jwt_required()
def create_ticket():
    data = request.get_json()
    ticket = Ticket(**data)
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket.to_dict()), 201

@tickets_bp.route('/<ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict()), 200

@tickets_bp.route('/<ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)
    db.session.commit()
    return jsonify(ticket.to_dict()), 200

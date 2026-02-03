from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.accounting import ChartOfAccounts, JournalEntry

accounting_bp = Blueprint('accounting', __name__)

@accounting_bp.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    accounts = ChartOfAccounts.query.all()
    return jsonify([{'id': str(a.id), 'code': a.account_code, 'name': a.account_name, 'type': a.account_type} for a in accounts]), 200

@accounting_bp.route('/journal-entries', methods=['GET'])
@jwt_required()
def get_journal_entries():
    entries = JournalEntry.query.all()
    return jsonify([{'id': str(e.id), 'number': e.entry_number, 'date': e.entry_date.isoformat(), 'status': e.status} for e in entries]), 200

@accounting_bp.route('/journal-entries', methods=['POST'])
@jwt_required()
def create_journal_entry():
    data = request.get_json()
    entry = JournalEntry(**data)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': str(entry.id), 'message': 'Journal entry created'}), 201

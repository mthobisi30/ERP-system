"""Global cross-entity search."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app.models.customer import Customer, Lead
from app.models.project import Project
from app.models.accounting import Invoice
from app.models.ticket import Ticket
from app.models.sales import Quotation

search_bp = Blueprint('search', __name__)


@search_bp.route('', methods=['GET'])
@jwt_required()
def search():
    q = (request.args.get('q') or '').strip()
    if len(q) < 2:
        return jsonify({'results': []}), 200
    like = f"%{q}%"
    results = []

    for c in Customer.query.filter(or_(
            Customer.company_name.ilike(like), Customer.customer_code.ilike(like),
            Customer.contact_person.ilike(like))).limit(6).all():
        label = (f"{c.customer_code} · " if c.customer_code else '') + (c.company_name or c.contact_person or '—')
        results.append({'type': 'Client', 'label': label, 'url': f'/customers/{c.id}'})

    for p in Project.query.filter(or_(
            Project.name.ilike(like), Project.project_code.ilike(like),
            Project.system_name.ilike(like))).limit(6).all():
        label = (f"{p.project_code} · " if p.project_code else '') + p.name
        results.append({'type': 'Project', 'label': label, 'url': f'/projects/{p.id}'})

    for i in Invoice.query.filter(Invoice.invoice_number.ilike(like)).limit(5).all():
        results.append({'type': 'Invoice', 'label': i.invoice_number, 'url': '/billing'})

    for t in Ticket.query.filter(or_(
            Ticket.ticket_number.ilike(like), Ticket.subject.ilike(like))).limit(5).all():
        url = f'/projects/{t.project_id}' if t.project_id else '/tickets'
        results.append({'type': 'Ticket', 'label': f"{t.ticket_number} · {t.subject}", 'url': url})

    for q_ in Quotation.query.filter(or_(
            Quotation.quote_number.ilike(like), Quotation.title.ilike(like))).limit(5).all():
        results.append({'type': 'Quote', 'label': f"{q_.quote_number} · {q_.title or ''}", 'url': '/quotations'})

    for l in Lead.query.filter(or_(
            Lead.contact_name.ilike(like), Lead.company_name.ilike(like))).limit(5).all():
        results.append({'type': 'Lead', 'label': l.contact_name or l.company_name or '—', 'url': '/leads'})

    return jsonify({'results': results, 'query': q}), 200

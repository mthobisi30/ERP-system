from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.sales import SalesOrder, Quotation, QuotationItem
from app.models.project import Project
from app.services.pdf_service import quote_pdf

sales_bp = Blueprint('sales', __name__)


def _money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _parse_date(value, default=None):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default


def _next_quote_number():
    return f"Q-{Quotation.query.count() + 1:05d}"

@sales_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_sales_orders():
    page = request.args.get('page', 1, type=int)
    orders = SalesOrder.query.paginate(page=page, per_page=20)
    return jsonify({'orders': [o.to_dict() for o in orders.items], 'total': orders.total}), 200

@sales_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_sales_order():
    data = request.get_json()
    order = SalesOrder(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201

@sales_bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_sales_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    return jsonify(order.to_dict()), 200

@sales_bp.route('/quotations', methods=['GET'])
@jwt_required()
def get_quotations():
    q = Quotation.query
    for field in ('status', 'customer_id'):
        if request.args.get(field):
            q = q.filter(getattr(Quotation, field) == request.args.get(field))
    quotes = q.order_by(Quotation.created_at.desc()).all()
    return jsonify({'quotations': [x.to_dict() for x in quotes], 'total': len(quotes)}), 200

@sales_bp.route('/quotations', methods=['POST'])
@jwt_required()
def create_quotation():
    """Create a quote from line items; VAT computed from subtotal + vat_rate."""
    data = request.get_json() or {}
    items = data.get('items', []) or []

    vat_enabled = current_app.config.get('VAT_ENABLED', True)
    default_vat = current_app.config.get('VAT_RATE', 15.0) if vat_enabled else 0
    vat_rate = Decimal(str(data.get('vat_rate', default_vat)))

    subtotal = Decimal('0.00')
    prepared = []
    for it in items:
        qty = Decimal(str(it.get('quantity', 0) or 0))
        price = Decimal(str(it.get('unit_price', 0) or 0))
        line = _money(qty * price)
        subtotal += line
        prepared.append((it.get('description'), qty, price, line))
    subtotal = _money(subtotal)
    vat_amount = _money(subtotal * vat_rate / Decimal('100'))

    quote = Quotation(
        quote_number=data.get('quote_number') or _next_quote_number(),
        title=data.get('title'),
        customer_id=data.get('customer_id'),
        quote_date=_parse_date(data.get('quote_date'), date.today()),
        valid_until=_parse_date(data.get('valid_until')),
        status='draft',
        subtotal=subtotal,
        vat_rate=vat_rate,
        tax_amount=vat_amount,
        total_amount=_money(subtotal + vat_amount),
        notes=data.get('notes'),
    )
    try:
        db.session.add(quote)
        db.session.flush()
        for desc, qty, price, line in prepared:
            db.session.add(QuotationItem(quotation_id=quote.id, description=desc,
                                         quantity=qty, unit_price=price, line_total=line))
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create quote', 'detail': str(exc)}), 400
    return jsonify(quote.to_dict()), 201

@sales_bp.route('/quotations/<quote_id>', methods=['GET'])
@jwt_required()
def get_quotation(quote_id):
    quote = Quotation.query.get_or_404(quote_id)
    items = QuotationItem.query.filter_by(quotation_id=quote.id).all()
    payload = quote.to_dict()
    payload['items'] = [i.to_dict() for i in items]
    return jsonify(payload), 200

@sales_bp.route('/quotations/<quote_id>/pdf', methods=['GET'])
@jwt_required()
def quotation_pdf_route(quote_id):
    pdf, number = quote_pdf(quote_id)
    if pdf is None:
        return jsonify({'error': 'Quote not found'}), 404
    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename="{number}.pdf"'})

@sales_bp.route('/quotations/<quote_id>/status', methods=['POST'])
@jwt_required()
def set_quotation_status(quote_id):
    """Move a quote to sent / declined / expired."""
    quote = Quotation.query.get_or_404(quote_id)
    new_status = (request.get_json() or {}).get('status')
    if new_status not in ('draft', 'sent', 'declined', 'expired'):
        return jsonify({'error': 'Invalid status'}), 400
    quote.status = new_status
    db.session.commit()
    return jsonify(quote.to_dict()), 200

@sales_bp.route('/quotations/<quote_id>/accept', methods=['POST'])
@jwt_required()
def accept_quotation(quote_id):
    """Accept a quote and spin up a fixed-price project from it."""
    quote = Quotation.query.get_or_404(quote_id)
    if quote.converted_project_id:
        return jsonify({'error': 'Quote already converted'}), 409
    data = request.get_json(silent=True) or {}
    project = Project(
        name=data.get('name') or quote.title or f"Project from {quote.quote_number}",
        customer_id=quote.customer_id,
        status='active',
        billing_type=data.get('billing_type', 'fixed_price'),
        budget=quote.total_amount,
        currency=data.get('currency', current_app.config.get('DEFAULT_CURRENCY', 'ZAR')),
    )
    quote.status = 'accepted'
    try:
        db.session.add(project)
        db.session.flush()
        quote.converted_project_id = project.id
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not accept quote', 'detail': str(exc)}), 400
    return jsonify({'message': 'Quote accepted', 'quote': quote.to_dict(),
                    'project': project.to_dict()}), 201

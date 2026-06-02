"""Invoice Routes — incl. generating invoices from unbilled time (ZAR + VAT)."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.accounting import Invoice, InvoiceItem
from app.services.billing_service import generate_invoice_from_unbilled_time, _next_invoice_number
from app.services.pdf_service import invoice_pdf

invoices_bp = Blueprint('invoices', __name__)


def _money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    q = Invoice.query
    for field in ('project_id', 'customer_id', 'status'):
        if request.args.get(field):
            q = q.filter(getattr(Invoice, field) == request.args.get(field))
    page = request.args.get('page', 1, type=int)
    invoices = q.order_by(Invoice.invoice_date.desc()).paginate(page=page, per_page=20)
    return jsonify({'invoices': [i.to_dict() for i in invoices.items], 'total': invoices.total}), 200


@invoices_bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create an invoice manually. VAT is computed from subtotal + vat_rate."""
    data = request.get_json() or {}
    vat_enabled = current_app.config.get('VAT_ENABLED', True)
    default_vat = current_app.config.get('VAT_RATE', 15.0) if vat_enabled else 0
    subtotal = _money(data.get('subtotal', 0))
    vat_rate = Decimal(str(data.get('vat_rate', default_vat)))
    vat_amount = _money(subtotal * vat_rate / Decimal('100'))

    invoice = Invoice(
        invoice_number=data.get('invoice_number') or _next_invoice_number(),
        customer_id=data.get('customer_id'),
        project_id=data.get('project_id'),
        invoice_date=date.fromisoformat(data['invoice_date']) if data.get('invoice_date') else date.today(),
        due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None,
        status=data.get('status', 'draft'),
        currency=data.get('currency', current_app.config.get('DEFAULT_CURRENCY', 'ZAR')),
        subtotal=subtotal,
        vat_rate=vat_rate,
        vat_amount=vat_amount,
        total_amount=_money(subtotal + vat_amount),
        notes=data.get('notes'),
    )
    try:
        db.session.add(invoice)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create invoice', 'detail': str(exc)}), 400
    return jsonify(invoice.to_dict()), 201


@invoices_bp.route('/generate-from-time', methods=['POST'])
@jwt_required()
def generate_from_time():
    """Generate a draft invoice from a project's unbilled billable time entries."""
    data = request.get_json() or {}
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    try:
        invoice = generate_invoice_from_unbilled_time(
            project_id,
            vat_rate=data.get('vat_rate'),
            due_days=data.get('due_days', 30),
            invoice_number=data.get('invoice_number'),
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not generate invoice', 'detail': str(exc)}), 400
    items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    return jsonify({
        'message': 'Invoice generated from unbilled time',
        'invoice': invoice.to_dict(),
        'items': [it.to_dict() for it in items],
    }), 201


@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
    payload = invoice.to_dict()
    payload['items'] = [it.to_dict() for it in items]
    return jsonify(payload), 200


@invoices_bp.route('/<invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    data = request.get_json() or {}
    for key in ('status', 'notes'):
        if key in data:
            setattr(invoice, key, data[key])
    if 'due_date' in data and data['due_date']:
        invoice.due_date = date.fromisoformat(data['due_date'])
    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update invoice', 'detail': str(exc)}), 400
    return jsonify(invoice.to_dict()), 200


@invoices_bp.route('/<invoice_id>/items', methods=['GET'])
@jwt_required()
def get_invoice_items(invoice_id):
    items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    return jsonify({'items': [it.to_dict() for it in items]}), 200


@invoices_bp.route('/<invoice_id>/pdf', methods=['GET'])
@jwt_required()
def invoice_pdf_route(invoice_id):
    pdf, number = invoice_pdf(invoice_id)
    if pdf is None:
        return jsonify({'error': 'Invoice not found'}), 404
    return Response(pdf, mimetype='application/pdf',
                    headers={'Content-Disposition': f'inline; filename="{number}.pdf"'})

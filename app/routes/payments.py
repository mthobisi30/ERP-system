"""Payment Routes — record payments and reconcile against invoices."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from config.database import db
from app.models.accounting import Payment, Invoice
from app.services.activity import record

payments_bp = Blueprint('payments', __name__)


def _money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _next_payment_number():
    return f"PAY-{Payment.query.count() + 1:05d}"


@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    q = Payment.query
    for field in ('invoice_id', 'customer_id'):
        if request.args.get(field):
            q = q.filter(getattr(Payment, field) == request.args.get(field))
    payments = q.order_by(Payment.payment_date.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments], 'total': len(payments)}), 200


@payments_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    """Record a payment. If linked to an invoice, update its paid amount/status."""
    data = request.get_json() or {}
    if data.get('amount') is None:
        return jsonify({'error': 'amount is required'}), 400

    invoice = None
    if data.get('invoice_id'):
        invoice = db.session.get(Invoice, data['invoice_id'])
        if invoice is None:
            return jsonify({'error': 'Invoice not found'}), 404

    payment = Payment(
        payment_number=data.get('payment_number') or _next_payment_number(),
        payment_type=data.get('payment_type', 'customer'),
        customer_id=data.get('customer_id') or (invoice.customer_id if invoice else None),
        invoice_id=data.get('invoice_id'),
        payment_date=date.fromisoformat(data['payment_date']) if data.get('payment_date') else date.today(),
        amount=_money(data['amount']),
        payment_method=data.get('payment_method'),
        reference=data.get('reference'),
    )

    try:
        db.session.add(payment)
        if invoice is not None:
            invoice.paid_amount = _money(Decimal(str(invoice.paid_amount or 0)) + _money(data['amount']))
            if invoice.paid_amount >= Decimal(str(invoice.total_amount or 0)) and invoice.total_amount:
                invoice.status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'partial'
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not record payment', 'detail': str(exc)}), 400

    record('payment.recorded', 'payment', payment.id,
           project_id=(invoice.project_id if invoice else None), customer_id=payment.customer_id,
           summary=f"Payment {payment.payment_number} — {float(payment.amount or 0):,.2f}"
                   + (f" against {invoice.invoice_number}" if invoice else ""))
    result = {'message': 'Payment recorded', 'payment': payment.to_dict()}
    if invoice is not None:
        result['invoice'] = invoice.to_dict()
    return jsonify(result), 201


@payments_bp.route('/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    return jsonify(Payment.query.get_or_404(payment_id).to_dict()), 200

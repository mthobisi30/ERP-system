"""Billing service for the agency spine.

Two responsibilities:
  * resolve_bill_rate() — work out what hourly rate applies to a person on a
    project, following the resolution chain.
  * generate_invoice_from_unbilled_time() — turn a project's unbilled billable
    time entries into a draft VAT invoice, linking each line back to its entry.
"""
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from flask import current_app

from config.database import db
from app.models.user import User
from app.models.project import Project, ProjectTeam
from app.models.rate import RateCard
from app.models.schedule import TimeEntry
from app.models.accounting import Invoice, InvoiceItem
from app.models.retainer import RetainerContract


def _money(value):
    """Round to 2 decimal places as a Decimal."""
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def resolve_bill_rate(user_id, project_id):
    """Return the bill rate (Decimal) for a user on a project, or None.

    Chain: ProjectTeam override -> RateCard(person) -> RateCard(role) ->
    Project.billing_rate.
    """
    if project_id:
        pt = ProjectTeam.query.filter_by(project_id=project_id, user_id=user_id).first()
        if pt and pt.hourly_rate is not None:
            return pt.hourly_rate

    rc = (RateCard.query
          .filter_by(user_id=user_id, is_active=True)
          .order_by(RateCard.effective_date.desc().nullslast())
          .first())
    if rc and rc.bill_rate is not None:
        return rc.bill_rate

    user = db.session.get(User, user_id)
    # Match the rate card against the person's job title/band (position),
    # falling back to the authz role only if no position is set.
    title = (user.position or user.role) if user else None
    if title:
        rc = (RateCard.query
              .filter(RateCard.role == title,
                      RateCard.user_id.is_(None),
                      RateCard.is_active.is_(True))
              .order_by(RateCard.effective_date.desc().nullslast())
              .first())
        if rc and rc.bill_rate is not None:
            return rc.bill_rate

    if project_id:
        proj = db.session.get(Project, project_id)
        if proj and proj.billing_rate is not None:
            return proj.billing_rate

    return None


def _next_invoice_number():
    seq = Invoice.query.count() + 1
    return f"INV-{seq:05d}"


def generate_invoice_from_unbilled_time(project_id, vat_rate=None, due_days=30,
                                        invoice_number=None, invoice_date=None):
    """Create a draft invoice from a project's unbilled, billable time entries.

    Each time entry becomes one invoice line (hours x bill_rate) and is marked
    invoiced. Returns the Invoice. Raises ValueError if there's nothing to bill.
    """
    project = db.session.get(Project, project_id)
    if project is None:
        raise ValueError('Project not found')

    entries = (TimeEntry.query
               .filter(TimeEntry.project_id == project_id,
                       TimeEntry.billable.is_(True),
                       TimeEntry.invoiced.is_(False),
                       TimeEntry.hours > 0)
               .order_by(TimeEntry.entry_date.asc())
               .all())
    if not entries:
        raise ValueError('No unbilled billable time entries for this project')

    if vat_rate is None:
        vat_rate = current_app.config.get('VAT_RATE', 15.0) if current_app.config.get('VAT_ENABLED', True) else 0
    vat_rate = Decimal(str(vat_rate))

    today = invoice_date or date.today()
    invoice = Invoice(
        invoice_number=invoice_number or _next_invoice_number(),
        customer_id=project.customer_id,
        project_id=project.id,
        invoice_date=today,
        due_date=today + timedelta(days=due_days),
        status='draft',
        currency=project.currency or current_app.config.get('DEFAULT_CURRENCY', 'ZAR'),
        vat_rate=vat_rate,
    )
    db.session.add(invoice)
    db.session.flush()  # assign invoice.id for the FK links

    subtotal = Decimal('0.00')
    for e in entries:
        rate = e.bill_rate if e.bill_rate is not None else Decimal('0')
        line_total = _money(Decimal(str(e.hours)) * Decimal(str(rate)))
        subtotal += line_total
        desc = e.description or 'Professional services'
        db.session.add(InvoiceItem(
            invoice_id=invoice.id,
            time_entry_id=e.id,
            description=f"{e.entry_date.isoformat()} — {desc} ({e.hours}h @ {rate})",
            quantity=e.hours,
            unit_price=rate,
            line_total=line_total,
        ))
        e.invoiced = True
        e.invoice_id = invoice.id

    subtotal = _money(subtotal)
    vat_amount = _money(subtotal * vat_rate / Decimal('100'))
    invoice.subtotal = subtotal
    invoice.vat_amount = vat_amount
    invoice.total_amount = _money(subtotal + vat_amount)

    db.session.commit()
    return invoice


def _period_bounds(period):
    """Return (first_day, last_day) for a 'YYYY-MM' period string."""
    year, month = (int(x) for x in period.split('-'))
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def current_period():
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


def run_retainers(period=None, due_days=14):
    """Generate invoices for active retainer contracts for a month.

    ``period`` is 'YYYY-MM' (defaults to the current month). Idempotent: a
    contract already invoiced for that period is skipped. Returns a summary.
    """
    period = period or current_period()
    p_start, p_end = _period_bounds(period)

    vat_enabled = current_app.config.get('VAT_ENABLED', True)
    vat_default = current_app.config.get('VAT_RATE', 15.0) if vat_enabled else 0
    default_currency = current_app.config.get('DEFAULT_CURRENCY', 'ZAR')

    contracts = RetainerContract.query.filter(RetainerContract.status == 'active').all()
    created, skipped = [], 0
    for contract in contracts:
        # Outside the contract's active date range, or already billed this period.
        if (contract.start_date and contract.start_date > p_end) or \
           (contract.end_date and contract.end_date < p_start) or \
           contract.last_invoiced_period == period:
            skipped += 1
            continue

        vat_rate = Decimal(str(vat_default)) if contract.vat_applicable else Decimal('0')
        subtotal = _money(contract.monthly_fee)
        vat_amount = _money(subtotal * vat_rate / Decimal('100'))

        invoice = Invoice(
            invoice_number=_next_invoice_number(),
            customer_id=contract.customer_id,
            project_id=contract.project_id,
            invoice_date=p_start,
            due_date=p_start + timedelta(days=due_days),
            status='draft',
            currency=contract.currency or default_currency,
            subtotal=subtotal,
            vat_rate=vat_rate,
            vat_amount=vat_amount,
            total_amount=_money(subtotal + vat_amount),
            notes=f"Retainer: {contract.name} — {period}",
        )
        db.session.add(invoice)
        db.session.flush()
        db.session.add(InvoiceItem(
            invoice_id=invoice.id,
            description=f"Monthly retainer — {contract.name} ({period})",
            quantity=1,
            unit_price=subtotal,
            line_total=subtotal,
        ))
        contract.last_invoiced_period = period
        created.append(invoice)

    db.session.commit()
    return {'period': period, 'created': created, 'skipped': skipped}

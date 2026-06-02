"""Retainer / recurring-revenue contracts (e.g. managed services, support)."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class RetainerContract(db.Model):
    __tablename__ = 'retainer_contracts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)              # e.g. "Acme — Managed Support"
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))  # optional link
    monthly_fee = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(10), default='ZAR')
    billing_day = db.Column(db.Integer, default=1)               # day of month to invoice
    vat_applicable = db.Column(db.Boolean, default=True, nullable=False)
    status = db.Column(db.String(20), default='active')          # active | paused | cancelled
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    # Last period (YYYY-MM) an invoice was generated for — guards against double-billing.
    last_invoiced_period = db.Column(db.String(7))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'project_id': str(self.project_id) if self.project_id else None,
            'monthly_fee': float(self.monthly_fee) if self.monthly_fee is not None else 0,
            'currency': self.currency,
            'billing_day': self.billing_day,
            'vat_applicable': self.vat_applicable,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'last_invoiced_period': self.last_invoiced_period,
            'notes': self.notes,
        }

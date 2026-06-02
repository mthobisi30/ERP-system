from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class ChartOfAccounts(db.Model):
    __tablename__ = 'chart_of_accounts'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntryLine(db.Model):
    __tablename__ = 'journal_entry_lines'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = db.Column(UUID(as_uuid=True), db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chart_of_accounts.id'))
    debit_amount = db.Column(db.Numeric(15, 2), default=0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')  # draft | sent | paid | overdue | cancelled
    currency = db.Column(db.String(10), default='ZAR')
    # Amounts: total = subtotal + vat_amount
    subtotal = db.Column(db.Numeric(15, 2), default=0)       # ex-VAT
    vat_rate = db.Column(db.Numeric(5, 2), default=15.0)     # percent
    vat_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)   # incl. VAT
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def balance_due(self):
        return float(self.total_amount or 0) - float(self.paid_amount or 0)

    def to_dict(self):
        return {
            'id': str(self.id),
            'invoice_number': self.invoice_number,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'project_id': str(self.project_id) if self.project_id else None,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'currency': self.currency,
            'subtotal': float(self.subtotal) if self.subtotal is not None else 0,
            'vat_rate': float(self.vat_rate) if self.vat_rate is not None else 0,
            'vat_amount': float(self.vat_amount) if self.vat_amount is not None else 0,
            'total_amount': float(self.total_amount) if self.total_amount is not None else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount is not None else 0,
            'balance_due': self.balance_due,
        }

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = db.Column(UUID(as_uuid=True), db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True))
    time_entry_id = db.Column(UUID(as_uuid=True), db.ForeignKey('time_entries.id'))
    description = db.Column(db.Text)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)  # e.g. hours
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)  # e.g. rate
    line_total = db.Column(db.Numeric(15, 2))

    def to_dict(self):
        return {
            'id': str(self.id),
            'invoice_id': str(self.invoice_id),
            'time_entry_id': str(self.time_entry_id) if self.time_entry_id else None,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity is not None else 0,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0,
            'line_total': float(self.line_total) if self.line_total is not None else 0,
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_type = db.Column(db.String(50), default='customer')  # customer | refund
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    invoice_id = db.Column(UUID(as_uuid=True), db.ForeignKey('invoices.id'))
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(50))
    reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'payment_number': self.payment_number,
            'payment_type': self.payment_type,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'invoice_id': str(self.invoice_id) if self.invoice_id else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount': float(self.amount) if self.amount is not None else 0,
            'payment_method': self.payment_method,
            'reference': self.reference,
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_number = db.Column(db.String(50), unique=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    description = db.Column(db.Text)
    expense_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    # billable = rechargeable to the client (passthrough); else it's an internal cost.
    billable = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending | approved | rejected
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'expense_number': self.expense_number,
            'project_id': str(self.project_id) if self.project_id else None,
            'description': self.description,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'category': self.category,
            'amount': float(self.amount) if self.amount is not None else 0,
            'billable': self.billable,
            'status': self.status,
        }

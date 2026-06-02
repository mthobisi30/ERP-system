from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Quotation(db.Model):
    __tablename__ = 'quotations'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200))
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    quote_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')  # draft | sent | accepted | declined | expired
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    vat_rate = db.Column(db.Numeric(5, 2), default=15.0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)   # VAT amount
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    converted_project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'quote_number': self.quote_number,
            'title': self.title,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'quote_date': self.quote_date.isoformat() if self.quote_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'subtotal': float(self.subtotal) if self.subtotal is not None else 0,
            'vat_rate': float(self.vat_rate) if self.vat_rate is not None else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount is not None else 0,
            'total_amount': float(self.total_amount) if self.total_amount is not None else 0,
            'notes': self.notes,
            'converted_project_id': str(self.converted_project_id) if self.converted_project_id else None,
        }

class QuotationItem(db.Model):
    __tablename__ = 'quotation_items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('quotations.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True))
    description = db.Column(db.Text)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    line_total = db.Column(db.Numeric(15, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity is not None else 0,
            'unit_price': float(self.unit_price) if self.unit_price is not None else 0,
            'line_total': float(self.line_total) if self.line_total is not None else 0,
        }

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    order_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_status = db.Column(db.String(50), default='unpaid')
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': str(self.id), 'order_number': self.order_number, 'status': self.status, 'total_amount': float(self.total_amount) if self.total_amount else 0}

class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True))
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    line_total = db.Column(db.Numeric(15, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

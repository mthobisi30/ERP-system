from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Quotation(db.Model):
    __tablename__ = 'quotations'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    quote_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': str(self.id), 'quote_number': self.quote_number, 'status': self.status, 'total_amount': float(self.total_amount) if self.total_amount else 0}

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

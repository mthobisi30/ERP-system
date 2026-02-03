from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code = db.Column(db.String(50), unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': str(self.id), 'supplier_code': self.supplier_code, 'company_name': self.company_name, 'status': self.status}

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('suppliers.id'))
    order_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='draft')
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': str(self.id), 'po_number': self.po_number, 'status': self.status, 'total_amount': float(self.total_amount) if self.total_amount else 0}

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True))
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    line_total = db.Column(db.Numeric(15, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoodsReceipt(db.Model):
    __tablename__ = 'goods_receipts'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    purchase_order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('purchase_orders.id'))
    receipt_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoodsReceiptItem(db.Model):
    __tablename__ = 'goods_receipt_items'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goods_receipt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('goods_receipts.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True))
    quantity_received = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

"""Product Models"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('product_categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('product_categories.id'))
    product_type = db.Column(db.String(50))
    unit_of_measure = db.Column(db.String(50))
    cost_price = db.Column(db.Numeric(15, 2))
    selling_price = db.Column(db.Numeric(15, 2))
    mrp = db.Column(db.Numeric(15, 2))
    tax_rate = db.Column(db.Numeric(5, 2))
    barcode = db.Column(db.String(100))
    weight = db.Column(db.Numeric(10, 2))
    dimensions = db.Column(JSONB)
    is_active = db.Column(db.Boolean, default=True)
    image_urls = db.Column(ARRAY(db.Text))
    specifications = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'selling_price': float(self.selling_price) if self.selling_price else None,
            'is_active': self.is_active
        }

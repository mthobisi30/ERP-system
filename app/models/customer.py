"""Customer and CRM Models"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_code = db.Column(db.String(50), unique=True)
    company_name = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    customer_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='active')
    billing_address = db.Column(JSONB)
    shipping_address = db.Column(JSONB)
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(100))
    credit_limit = db.Column(db.Numeric(15, 2))
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_code': self.customer_code,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerContact(db.Model):
    __tablename__ = 'customer_contacts'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_code = db.Column(db.String(50), unique=True)
    company_name = db.Column(db.String(200))
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), default='new')
    interest_level = db.Column(db.String(20))
    estimated_value = db.Column(db.Numeric(15, 2))
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    converted_to_customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    notes = db.Column(db.Text)
    next_follow_up = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'lead_code': self.lead_code,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_code = db.Column(db.String(50), unique=True)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    lead_id = db.Column(UUID(as_uuid=True), db.ForeignKey('leads.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    stage = db.Column(db.String(50), default='prospecting')
    probability = db.Column(db.Integer, default=0)
    estimated_value = db.Column(db.Numeric(15, 2))
    expected_close_date = db.Column(db.Date)
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'opportunity_code': self.opportunity_code,
            'name': self.name,
            'stage': self.stage,
            'estimated_value': float(self.estimated_value) if self.estimated_value else None,
            'status': self.status
        }

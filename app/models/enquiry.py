"""Enquiry model — contact-form / website enquiries surfaced in the ERP."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    company = db.Column(db.String(200))
    subject = db.Column(db.String(250))
    message = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), default='website')
    status = db.Column(db.String(20), default='new')  # new | read | responded | archived
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'subject': self.subject,
            'message': self.message,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

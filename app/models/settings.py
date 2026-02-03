from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class CompanySettings(db.Model):
    __tablename__ = 'company_settings'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = db.Column(db.String(200))
    logo_url = db.Column(db.Text)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    currency = db.Column(db.String(10), default='USD')
    timezone = db.Column(db.String(50))
    settings = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

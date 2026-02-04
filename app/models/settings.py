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

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), unique=True, nullable=False)
    theme = db.Column(db.String(20), default='light')  # 'light' or 'dark'
    language = db.Column(db.String(10), default='en')
    region = db.Column(db.String(10), default='US')
    currency = db.Column(db.String(10), default='USD')
    date_format = db.Column(db.String(20), default='YYYY-MM-DD')
    time_format = db.Column(db.String(10), default='24h')
    notifications_enabled = db.Column(db.Boolean, default=True)
    sidebar_collapsed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'theme': self.theme,
            'language': self.language,
            'region': self.region,
            'currency': self.currency,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'notifications_enabled': self.notifications_enabled,
            'sidebar_collapsed': self.sidebar_collapsed
        }

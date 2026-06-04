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
    # --- Issuer / letterhead (drives generated documents) ---
    legal_name = db.Column(db.String(250))            # e.g. "Rephina Software Solutions (PTY) LTD"
    registration_number = db.Column(db.String(60))    # e.g. "2026/250285/07"
    tax_number = db.Column(db.String(60))             # SARS income tax reference no.
    signatory_name = db.Column(db.String(150))        # who signs documents
    address = db.Column(db.Text)                       # full postal/physical address
    website = db.Column(db.String(200))
    vat_registered = db.Column(db.Boolean, default=True, nullable=False)
    vat_number = db.Column(db.String(60))
    doc_ref_prefix = db.Column(db.String(10), default='RSS')  # RSS-INV-2026-001
    # Banking (for invoices)
    bank_name = db.Column(db.String(120))
    bank_account_name = db.Column(db.String(150))
    bank_account_number = db.Column(db.String(40))
    bank_branch_code = db.Column(db.String(20))
    bank_account_type = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'company_name': self.company_name,
            'legal_name': self.legal_name,
            'registration_number': self.registration_number,
            'tax_number': self.tax_number,
            'signatory_name': self.signatory_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'currency': self.currency,
            'timezone': self.timezone,
            'vat_registered': self.vat_registered,
            'vat_number': self.vat_number,
            'doc_ref_prefix': self.doc_ref_prefix,
            'bank_name': self.bank_name,
            'bank_account_name': self.bank_account_name,
            'bank_account_number': self.bank_account_number,
            'bank_branch_code': self.bank_branch_code,
            'bank_account_type': self.bank_account_type,
        }

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

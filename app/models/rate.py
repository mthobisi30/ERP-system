"""Rate Card Models — default billing/cost rates for an agency.

Rate resolution for a time entry goes:
  1. ProjectTeam.hourly_rate (per-project, per-person override)
  2. RateCard for the user (person-specific)
  3. RateCard for the user's role
  4. Project.billing_rate (project fallback)
"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class RateCard(db.Model):
    __tablename__ = 'rate_cards'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150), nullable=False)          # e.g. "Senior Developer"
    role = db.Column(db.String(100))                          # matches users.role / position
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))  # person-specific override
    bill_rate = db.Column(db.Numeric(10, 2), nullable=False)  # what the client pays
    cost_rate = db.Column(db.Numeric(10, 2))                  # internal cost (for margin)
    currency = db.Column(db.String(10), default='ZAR')
    unit = db.Column(db.String(10), default='hour')           # hour | day
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    effective_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role,
            'user_id': str(self.user_id) if self.user_id else None,
            'bill_rate': float(self.bill_rate) if self.bill_rate is not None else None,
            'cost_rate': float(self.cost_rate) if self.cost_rate is not None else None,
            'currency': self.currency,
            'unit': self.unit,
            'is_active': self.is_active,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
        }

from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100))
    entity_id = db.Column(UUID(as_uuid=True))
    old_values = db.Column(JSONB)
    new_values = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_level = db.Column(db.String(20))
    module = db.Column(db.String(100))
    message = db.Column(db.Text)
    extra_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

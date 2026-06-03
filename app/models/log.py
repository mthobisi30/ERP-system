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
    # Scope the trail to a project / client so it shows on those 360 views.
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    summary = db.Column(db.Text)
    old_values = db.Column(JSONB)
    new_values = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'project_id': str(self.project_id) if self.project_id else None,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_level = db.Column(db.String(20))
    module = db.Column(db.String(100))
    message = db.Column(db.Text)
    extra_data = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

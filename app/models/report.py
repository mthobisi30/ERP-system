from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(100))
    query_definition = db.Column(JSONB)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DashboardWidget(db.Model):
    __tablename__ = 'dashboard_widgets'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    widget_type = db.Column(db.String(100))
    title = db.Column(db.String(200))
    configuration = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

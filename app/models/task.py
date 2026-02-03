"""Task Management Models"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_code = db.Column(db.String(50), unique=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    milestone_id = db.Column(UUID(as_uuid=True), db.ForeignKey('milestones.id'))
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='todo')
    priority = db.Column(db.String(20), default='medium')
    estimated_hours = db.Column(db.Numeric(8, 2))
    actual_hours = db.Column(db.Numeric(8, 2), default=0)
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    tags = db.Column(ARRAY(db.Text))
    attachments = db.Column(JSONB)
    parent_task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'task_code': self.task_code,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TaskComment(db.Model):
    __tablename__ = 'task_comments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TaskAttachment(db.Model):
    __tablename__ = 'task_attachments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'), nullable=False)
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.Text)
    file_size = db.Column(db.BigInteger)
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

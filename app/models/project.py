"""
Project Management Models
"""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(50), default='planning')
    priority = db.Column(db.String(20), default='medium')
    project_manager_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    department_id = db.Column(UUID(as_uuid=True), db.ForeignKey('departments.id'))
    budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2), default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    completion_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'project_code': self.project_code,
            'status': self.status,
            'priority': self.priority,
            'budget': float(self.budget) if self.budget else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'completion_percentage': self.completion_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProjectTeam(db.Model):
    __tablename__ = 'project_team'
    
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(100))
    hourly_rate = db.Column(db.Numeric(10, 2))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

class Milestone(db.Model):
    __tablename__ = 'milestones'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')
    completion_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'name': self.name,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status
        }

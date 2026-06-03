from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customers.id'))
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='open')  # open | in_progress | resolved | closed
    category = db.Column(db.String(100))
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    due_date = db.Column(db.DateTime)                  # SLA target
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'ticket_number': self.ticket_number,
            'customer_id': str(self.customer_id) if self.customer_id else None,
            'project_id': str(self.project_id) if self.project_id else None,
            'subject': self.subject,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    response = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

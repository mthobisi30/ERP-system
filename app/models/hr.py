from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class PerformanceReview(db.Model):
    __tablename__ = 'performance_reviews'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    review_date = db.Column(db.Date)
    overall_rating = db.Column(db.Numeric(3, 2))
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = db.Column(UUID(as_uuid=True), db.ForeignKey('performance_reviews.id'), nullable=False)
    metric_name = db.Column(db.String(100))
    metric_value = db.Column(db.Numeric(10, 2))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Leave(db.Model):
    __tablename__ = 'leaves'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

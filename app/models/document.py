from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.BigInteger)
    category = db.Column(db.String(100))
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    tags = db.Column(ARRAY(db.Text))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

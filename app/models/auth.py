"""Auth support models."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TokenBlocklist(db.Model):
    """Revoked JWT IDs (jti). A token whose jti is here is rejected.

    DB-backed so revocation survives across serverless instances/restarts.
    """
    __tablename__ = 'token_blocklist'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = db.Column(db.String(64), nullable=False, unique=True, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

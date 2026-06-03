"""Generated project documents — registry + auto numbering (RSS-TYPE-YYYY-NNN)."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# doc_type codes used in the reference number
DOC_TYPES = {
    'INV': 'Invoice',
    'MILE': 'Milestone Completion Report',
    'END': 'Endorsement',
    'PMN': 'Project Migration Notice',
    'QUO': 'Quotation',
    'BRD': 'Business Requirements Document',
}


class ProjectDocument(db.Model):
    __tablename__ = 'project_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    doc_type = db.Column(db.String(10), nullable=False)   # INV | MILE | END | PMN ...
    doc_ref = db.Column(db.String(60), unique=True, nullable=False)  # RSS-INV-2026-004
    year = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(250))
    data = db.Column(JSONB)            # snapshot / free-form fields (endorsement, PMN)
    status = db.Column(db.String(30), default='issued')
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'project_id': str(self.project_id) if self.project_id else None,
            'doc_type': self.doc_type,
            'doc_type_label': DOC_TYPES.get(self.doc_type, self.doc_type),
            'doc_ref': self.doc_ref,
            'title': self.title,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def next_ref(doc_type, prefix='RSS', year=None):
        """Return the next reference like RSS-INV-2026-004 (per type, per year)."""
        year = year or datetime.utcnow().year
        last = (ProjectDocument.query
                .filter_by(doc_type=doc_type, year=year)
                .order_by(ProjectDocument.sequence.desc())
                .first())
        seq = (last.sequence + 1) if last else 1
        return f"{prefix}-{doc_type}-{year}-{seq:03d}", seq

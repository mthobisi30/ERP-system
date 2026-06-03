"""Blog / CMS models — posts authored in the ERP for the public website."""
from config.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(280), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    body = db.Column(db.Text)
    cover_image_url = db.Column(db.Text)
    tags = db.Column(db.String(300))  # comma-separated
    status = db.Column(db.String(20), default='draft')  # draft | published
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, full=False):
        data = {
            'id': str(self.id),
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'cover_image_url': self.cover_image_url,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()],
            'status': self.status,
            'author_id': str(self.author_id) if self.author_id else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if full:
            data['body'] = self.body
        return data

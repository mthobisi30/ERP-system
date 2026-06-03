"""Public (unauthenticated) endpoints for the website to consume.

- Published blog posts (read-only).
- Contact-form enquiry submission (rate-limited).
"""
from flask import Blueprint, request, jsonify

from config.database import db
from app.models.blog import BlogPost
from app.models.enquiry import Enquiry
from app.models.project import Project
from app.extensions import limiter

public_bp = Blueprint('public', __name__)


def _showcase_dict(p):
    """Public-safe projection of a project — no client names or financials."""
    return {
        'title': p.system_name or p.name,
        'project_type': p.project_type,
        'tech_stack': [t.strip() for t in (p.tech_stack or '').split(',') if t.strip()],
        'scope': p.scope,
        'live_url': p.live_url,
        'repository_url': p.repository_url,
        'status': p.status,
    }


@public_bp.route('/showcase', methods=['GET'])
def public_showcase():
    projects = (Project.query.filter_by(showcase=True)
                .order_by(Project.created_at.desc()).all())
    return jsonify({'projects': [_showcase_dict(p) for p in projects]}), 200


@public_bp.route('/blog', methods=['GET'])
def public_blog_list():
    posts = (BlogPost.query
             .filter_by(status='published')
             .order_by(BlogPost.published_at.desc().nullslast())
             .all())
    return jsonify({'posts': [p.to_dict() for p in posts]}), 200


@public_bp.route('/blog/<slug>', methods=['GET'])
def public_blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, status='published').first()
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify(post.to_dict(full=True)), 200


@public_bp.route('/enquiries', methods=['POST'])
@limiter.limit("20 per hour")
def submit_enquiry():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('message'):
        return jsonify({'error': 'name and message are required'}), 400
    enquiry = Enquiry(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone'),
        company=data.get('company'),
        subject=data.get('subject'),
        message=data['message'],
        source=data.get('source', 'website'),
        status='new',
    )
    try:
        db.session.add(enquiry)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not submit enquiry', 'detail': str(exc)}), 400
    return jsonify({'message': 'Thank you — we will be in touch within one business day.'}), 201

"""Blog management routes (authoring for the public website)."""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from slugify import slugify

from config.database import db
from app.models.blog import BlogPost

blog_bp = Blueprint('blog', __name__)

_ALLOWED = {'title', 'excerpt', 'body', 'cover_image_url', 'tags', 'status'}


def _unique_slug(title, current_id=None):
    base = slugify(title or 'post') or 'post'
    slug = base
    i = 2
    while True:
        existing = BlogPost.query.filter_by(slug=slug).first()
        if not existing or str(existing.id) == str(current_id):
            return slug
        slug = f"{base}-{i}"
        i += 1


@blog_bp.route('', methods=['GET'])
@jwt_required()
def list_posts():
    q = BlogPost.query
    if request.args.get('status'):
        q = q.filter_by(status=request.args.get('status'))
    posts = q.order_by(BlogPost.created_at.desc()).all()
    return jsonify({'posts': [p.to_dict() for p in posts], 'total': len(posts)}), 200


@blog_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json() or {}
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    post = BlogPost(author_id=get_jwt_identity(), slug=_unique_slug(data['title']))
    for k in _ALLOWED:
        if k in data:
            setattr(post, k, data[k])
    if post.status == 'published' and not post.published_at:
        post.published_at = datetime.utcnow()
    try:
        db.session.add(post)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create post', 'detail': str(exc)}), 400
    return jsonify(post.to_dict(full=True)), 201


@blog_bp.route('/<post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    return jsonify(BlogPost.query.get_or_404(post_id).to_dict(full=True)), 200


@blog_bp.route('/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json() or {}
    for k in _ALLOWED:
        if k in data:
            setattr(post, k, data[k])
    if 'title' in data:
        post.slug = _unique_slug(data['title'], current_id=post.id)
    if post.status == 'published' and not post.published_at:
        post.published_at = datetime.utcnow()
    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update post', 'detail': str(exc)}), 400
    return jsonify(post.to_dict(full=True)), 200


@blog_bp.route('/<post_id>/publish', methods=['POST'])
@jwt_required()
def publish_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    publish = (request.get_json(silent=True) or {}).get('publish', True)
    post.status = 'published' if publish else 'draft'
    post.published_at = datetime.utcnow() if publish else None
    db.session.commit()
    return jsonify(post.to_dict()), 200


@blog_bp.route('/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'}), 200

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.document import Document

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('', methods=['GET'])
@jwt_required()
def get_documents():
    documents = Document.query.all()
    return jsonify([{'id': str(d.id), 'name': d.name, 'file_type': d.file_type, 'category': d.category} for d in documents]), 200

@documents_bp.route('', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = get_jwt_identity()
    data = request.get_json()
    data['uploaded_by'] = user_id
    document = Document(**data)
    db.session.add(document)
    db.session.commit()
    return jsonify({'id': str(document.id), 'message': 'Document uploaded'}), 201

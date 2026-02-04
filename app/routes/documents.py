from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.document import Document
from app.services.storage_service import StorageService

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('', methods=['GET'])
@jwt_required()
def get_documents():
    documents = Document.query.all()
    return jsonify([{'id': str(d.id), 'name': d.name, 'file_type': d.file_type, 'category': d.category, 'file_url': getattr(d, 'file_url', None)} for d in documents]), 200

@documents_bp.route('', methods=['POST'])
@jwt_required()
def upload_document():
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    category = request.form.get('category', 'general')
    
    try:
        # Upload using StorageService
        file_url = StorageService.upload_file(file, folder='documents')
        
        document = Document(
            name=file.filename,
            file_type=file.content_type,
            category=category,
            uploaded_by=user_id,
            # We assume the model has a file_url field now, or we'll add it
        )
        # For this demo, let's assume we store the URL in a flexible metadata field if file_url doesn't exist
        # But ideally we should update the model. I'll check the model next.
        if hasattr(document, 'file_url'):
            document.file_url = file_url
            
        db.session.add(document)
        db.session.commit()
        return jsonify({'id': str(document.id), 'url': file_url, 'message': 'Document uploaded successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

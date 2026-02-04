import os
import cloudinary
import cloudinary.uploader
import boto3
from flask import current_app
from werkzeug.utils import secure_filename
import uuid

class StorageService:
    @staticmethod
    def get_provider():
        if current_app.config.get('CLOUDINARY_URL'):
            return 'cloudinary'
        if current_app.config.get('AWS_ACCESS_KEY_ID'):
            return 's3'
        return 'local'

    @staticmethod
    def upload_file(file, folder='documents'):
        provider = StorageService.get_provider()
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        if provider == 'cloudinary':
            cloudinary.config(
                cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
                api_key=current_app.config['CLOUDINARY_API_KEY'],
                api_secret=current_app.config['CLOUDINARY_API_SECRET']
            )
            upload_result = cloudinary.uploader.upload(file, folder=folder)
            return upload_result.get('secure_url')

        elif provider == 's3':
            s3 = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_S3_REGION']
            )
            s3.upload_fileobj(
                file,
                current_app.config['AWS_S3_BUCKET'],
                f"{folder}/{unique_filename}",
                ExtraArgs={'ACL': 'public-read'}
            )
            return f"https://{current_app.config['AWS_S3_BUCKET']}.s3.{current_app.config['AWS_S3_REGION']}.amazonaws.com/{folder}/{unique_filename}"

        else: # Local fallback
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            full_path = os.path.join(upload_path, unique_filename)
            file.save(full_path)
            return f"/uploads/{folder}/{unique_filename}"

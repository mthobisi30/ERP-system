"""
Application Configuration
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '1') == '1'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@rephinasoftware.com')
    
    # Redis (Cache)
    REDIS_URL = os.getenv('REDIS_URL')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')
    
    # Cloudinary (Alternative Storage)
    CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # External APIs
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    MAPS_API_KEY = os.getenv('MAPS_API_KEY')
    
    # Company
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Rephina Software')
    COMPANY_EMAIL = os.getenv('COMPANY_EMAIL', 'contact@rephinasoftware.com')
    COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE', 'https://www.rephinasoftware.com')

    # Localisation (South Africa defaults)
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'ZAR')
    CURRENCY_SYMBOL = os.getenv('CURRENCY_SYMBOL', 'R')
    TIMEZONE = os.getenv('TIMEZONE', 'Africa/Johannesburg')
    LOCALE = os.getenv('LOCALE', 'en_ZA')

    # VAT (South African VAT is 15%)
    VAT_ENABLED = os.getenv('VAT_ENABLED', '1') == '1'
    VAT_RATE = float(os.getenv('VAT_RATE', '15.0'))  # percent
    VAT_REGISTRATION_NUMBER = os.getenv('VAT_REGISTRATION_NUMBER', '')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

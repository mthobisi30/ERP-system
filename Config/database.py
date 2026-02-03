"""
Database Configuration and Initialization
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Import all models here to ensure they're registered
        from app.models import (
            user, project, task, customer, product, 
            inventory, sales, purchase, accounting, hr, ticket
        )
        
        # Create all tables (for development only)
        # In production, use migrations
        # db.create_all()
    
    return db

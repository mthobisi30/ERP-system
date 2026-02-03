#!/usr/bin/env python3
"""Database Seeding Script"""
import sys
sys.path.insert(0, '/home/claude/erp-system')

from app import app
from config.database import db
from app.models.user import User, Role
from app.models.settings import CompanySettings
from flask_bcrypt import generate_password_hash

def seed_roles():
    """Create default roles"""
    roles = [
        {'name': 'Administrator', 'description': 'Full system access'},
        {'name': 'Manager', 'description': 'Department management'},
        {'name': 'Employee', 'description': 'Basic employee access'}
    ]
    
    for role_data in roles:
        if not Role.query.filter_by(name=role_data['name']).first():
            role = Role(**role_data)
            db.session.add(role)
    db.session.commit()
    print("✅ Roles seeded")

def seed_admin_user():
    """Create default admin user"""
    if not User.query.filter_by(email='admin@erp.com').first():
        admin = User(
            email='admin@erp.com',
            username='admin',
            password_hash=generate_password_hash('Admin@123').decode('utf-8'),
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin@erp.com / Admin@123")

def seed_company_settings():
    """Create default company settings"""
    if not CompanySettings.query.first():
        settings = CompanySettings(
            company_name='My Company',
            email='contact@company.com',
            currency='USD',
            timezone='UTC'
        )
        db.session.add(settings)
        db.session.commit()
        print("✅ Company settings created")

def main():
    with app.app_context():
        print("🌱 Seeding database...")
        seed_roles()
        seed_admin_user()
        seed_company_settings()
        print("✅ Database seeding complete!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Create Admin User Script"""
import sys
sys.path.insert(0, '/home/claude/erp-system')

from app import app
from config.database import db
from app.models.user import User
from flask_bcrypt import generate_password_hash
import getpass

def create_admin():
    with app.app_context():
        email = input("Admin email: ")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        if User.query.filter_by(email=email).first():
            print("❌ User with this email already exists!")
            return
        
        admin = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password).decode('utf-8'),
            role='admin',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin user created: {email}")

if __name__ == '__main__':
    create_admin()

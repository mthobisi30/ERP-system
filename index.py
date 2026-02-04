"""
Main Flask Application Entry Point
Rephina Software ERP
"""
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = os.getenv('DEBUG', '0') == '1'

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": os.getenv('CORS_ORIGINS', '*').split(',')}})
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Email config
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', '1') == '1',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@rephina.com')
)
from app.services.email_service import mail
mail.init_app(app)

# Import database
from config.database import db, init_db

# Initialize database
init_db(app)

# Import blueprints
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.dashboard import dashboard_bp
from app.routes.projects import projects_bp
from app.routes.tasks import tasks_bp
from app.routes.schedule import schedule_bp
from app.routes.time_tracking import time_tracking_bp
from app.routes.customers import customers_bp
from app.routes.leads import leads_bp
from app.routes.opportunities import opportunities_bp
from app.routes.products import products_bp
from app.routes.inventory import inventory_bp
from app.routes.sales import sales_bp
from app.routes.procurement import procurement_bp
from app.routes.suppliers import suppliers_bp
from app.routes.accounting import accounting_bp
from app.routes.invoices import invoices_bp
from app.routes.payments import payments_bp
from app.routes.expenses import expenses_bp
from app.routes.hr import hr_bp
from app.routes.tickets import tickets_bp
from app.routes.reports import reports_bp
from app.routes.notifications import notifications_bp
from app.routes.documents import documents_bp
from app.routes.settings import settings_bp
from app.routes.logs import logs_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(projects_bp, url_prefix='/api/projects')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
app.register_blueprint(time_tracking_bp, url_prefix='/api/time-tracking')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(leads_bp, url_prefix='/api/leads')
app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
app.register_blueprint(sales_bp, url_prefix='/api/sales')
app.register_blueprint(procurement_bp, url_prefix='/api/procurement')
app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
app.register_blueprint(accounting_bp, url_prefix='/api/accounting')
app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
app.register_blueprint(hr_bp, url_prefix='/api/hr')
app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(documents_bp, url_prefix='/api/documents')
app.register_blueprint(settings_bp, url_prefix='/api/settings')
app.register_blueprint(logs_bp, url_prefix='/api/logs')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

# Root route - Serve Frontend
@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html', title='Dashboard', active_view='dashboard', api_endpoint='/dashboard/stats', view_key='stats')

@app.route('/tools')
def tools_page():
    return render_template('tools.html', title='Tools & Generators', active_view='tools', api_endpoint=None, view_key=None)

@app.route('/profile')
def profile_page():
    return render_template('profile.html', title='User Profile', active_view='profile', api_endpoint='/auth/me', view_key='user')

# Generic route for all list views
@app.route('/<view_name>')
def list_view(view_name):
    # Map view names to API endpoints/titles
    VIEW_CONFIG = {
        'projects': {'title': 'Projects', 'endpoint': '/projects', 'key': 'projects'},
        'tasks': {'title': 'Tasks', 'endpoint': '/tasks', 'key': 'tasks'},
        'schedule': {'title': 'Schedule', 'endpoint': '/schedule', 'key': 'events'},
        'documents': {'title': 'Documents', 'endpoint': '/documents', 'key': 'documents'},
        'customers': {'title': 'Customers', 'endpoint': '/customers', 'key': 'customers'},
        'leads': {'title': 'Leads', 'endpoint': '/leads', 'key': 'leads'},
        'opportunities': {'title': 'Opportunities', 'endpoint': '/opportunities', 'key': 'opportunities'},
        'sales': {'title': 'Sales Orders', 'endpoint': '/sales/orders', 'key': 'orders'},
        'quotations': {'title': 'Quotations', 'endpoint': '/sales/quotations', 'key': 'quotations'},
        'products': {'title': 'Products', 'endpoint': '/products', 'key': 'products'},
        'inventory': {'title': 'Stock Levels', 'endpoint': '/inventory', 'key': 'items'},
        'warehouses': {'title': 'Warehouses', 'endpoint': '/inventory/warehouses', 'key': 'warehouses'},
        'procurement': {'title': 'Purchase Orders', 'endpoint': '/procurement/purchase-orders', 'key': 'orders'},
        'suppliers': {'title': 'Suppliers', 'endpoint': '/suppliers', 'key': 'suppliers'},
        'accounting': {'title': 'Chart of Accounts', 'endpoint': '/accounting/accounts', 'key': 'accounts'},
        'journal_entries': {'title': 'Journal Entries', 'endpoint': '/accounting/journal-entries', 'key': 'entries'},
        'invoices': {'title': 'Invoices', 'endpoint': '/invoices', 'key': 'invoices'},
        'payments': {'title': 'Payments', 'endpoint': '/payments', 'key': 'payments'},
        'expenses': {'title': 'Expenses', 'endpoint': '/expenses', 'key': 'expenses'},
        'hr': {'title': 'Employees', 'endpoint': '/hr', 'key': 'employees'},
        'attendance': {'title': 'Attendance', 'endpoint': '/hr/attendance', 'key': 'attendance'},
        'leaves': {'title': 'Leaves', 'endpoint': '/hr/leaves', 'key': 'leaves'},
        'performance': {'title': 'Performance', 'endpoint': '/hr/performance-reviews', 'key': 'reviews'},
        'users': {'title': 'Users', 'endpoint': '/users', 'key': 'users'},
        'time-tracking': {'title': 'Time Tracking', 'endpoint': '/time-tracking', 'key': 'entries'},
        'tickets': {'title': 'Tickets', 'endpoint': '/tickets', 'key': 'tickets'},
        'notifications': {'title': 'Notifications', 'endpoint': '/notifications', 'key': 'notifications'},
        'reports': {'title': 'Reports', 'endpoint': '/reports', 'key': 'reports'},
        'logs': {'title': 'Logs', 'endpoint': '/logs/system', 'key': 'logs'},
        'settings': {'title': 'Settings', 'endpoint': '/settings', 'key': 'settings'},
    }

    if view_name in VIEW_CONFIG:
        config = VIEW_CONFIG[view_name]
        return render_template('list_view.html', 
                             title=config['title'], 
                             active_view=view_name, 
                             api_endpoint=config['endpoint'], 
                             view_key=config['key'])
    
    return "Page not found", 404

# API Documentation / Health
@app.route('/api')
def api_index():
    return jsonify({
        'message': 'ERP System API',
        'version': '1.0',
        'endpoints': {
            'products': '/api/products',
            'inventory': '/api/inventory',
            'sales': '/api/sales',
            'procurement': '/api/procurement',
            'suppliers': '/api/suppliers',
            'accounting': '/api/accounting',
            'invoices': '/api/invoices',
            'payments': '/api/payments',
            'expenses': '/api/expenses',
            'hr': '/api/hr',
            'tickets': '/api/tickets',
            'reports': '/api/reports',
            'notifications': '/api/notifications',
            'documents': '/api/documents',
            'settings': '/api/settings',
            'logs': '/api/logs'
        }
    })

# Health check
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'connected'}), 200

# Database test
@app.route('/api/db-test')
def db_test():
    try:
        # Test database connection
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        return jsonify({'database': 'connected', 'test': 'passed'}), 200
    except Exception as e:
        return jsonify({'database': 'error', 'message': str(e)}), 500

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired', 'message': 'Please log in again'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token', 'message': str(error)}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization required', 'message': 'No token provided'}), 401

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', '0') == '1', host='0.0.0.0', port=5000)

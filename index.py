"""
Main Flask Application Entry Point
Rephina Software ERP
"""
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

from app.extensions import limiter

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration — load the full Config class (DB, JWT, mail, storage, Stripe,
# company branding, ZAR/VAT localisation) from a single source of truth.
from config.config import config as config_map
config_env = os.getenv('FLASK_ENV', 'production' if os.getenv('DEBUG', '0') != '1' else 'development')
app.config.from_object(config_map.get(config_env, config_map['default']))


def _check_production_config(application):
    """Warn loudly about insecure defaults when running outside debug."""
    if application.config.get('DEBUG'):
        return
    issues = []
    if str(application.config.get('SECRET_KEY', '')).startswith('dev-'):
        issues.append('SECRET_KEY is an insecure default — set a strong SECRET_KEY.')
    if str(application.config.get('JWT_SECRET_KEY', '')).startswith('dev-'):
        issues.append('JWT_SECRET_KEY is an insecure default — set a strong JWT_SECRET_KEY.')
    db_url = application.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if not db_url or 'user:password@host' in db_url:
        issues.append('DATABASE_URL is not configured (still the placeholder).')
    if application.config.get('CORS_ORIGINS') == '*':
        issues.append('CORS_ORIGINS is "*" — restrict to your domain(s) in production.')
    for issue in issues:
        print(f"[CONFIG WARNING] {issue}")


_check_production_config(app)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS'].split(',')}})
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
limiter.init_app(app)

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
from app.routes.rates import rates_bp
from app.routes.retainers import retainers_bp
from app.routes.sales import sales_bp
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
from app.routes.blog import blog_bp
from app.routes.enquiries import enquiries_bp
from app.routes.modules import modules_bp
from app.routes.public import public_bp
from app.routes.search import search_bp

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
app.register_blueprint(rates_bp, url_prefix='/api/rates')
app.register_blueprint(retainers_bp, url_prefix='/api/retainers')
app.register_blueprint(sales_bp, url_prefix='/api/sales')
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
app.register_blueprint(blog_bp, url_prefix='/api/blog')
app.register_blueprint(enquiries_bp, url_prefix='/api/enquiries')
app.register_blueprint(modules_bp, url_prefix='/api/modules')
app.register_blueprint(public_bp, url_prefix='/api/public')
app.register_blueprint(search_bp, url_prefix='/api/search')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    # Don't leak internal details to clients in production.
    message = str(error) if app.debug else 'An unexpected error occurred'
    return jsonify({'error': 'Internal server error', 'message': message}), 500

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
    return render_template('tools.html', title='Tools & Generators', active_view='tools', api_endpoint='', view_key='')

@app.route('/profile')
def profile_page():
    return render_template('profile.html', title='User Profile', active_view='profile', api_endpoint='', view_key='user')

@app.route('/settings')
def settings_page():
    return render_template('settings.html', title='System Settings', active_view='settings', api_endpoint='', view_key='')

@app.route('/timesheet')
def timesheet_page():
    return render_template('timesheet.html', title='Timesheet', active_view='timesheet', api_endpoint='', view_key='')

@app.route('/billing')
def billing_page():
    return render_template('billing.html', title='Billing', active_view='billing', api_endpoint='', view_key='')

@app.route('/retainers')
def retainers_page():
    return render_template('retainers.html', title='Retainers', active_view='retainers', api_endpoint='', view_key='')

@app.route('/reports')
def reports_page():
    return render_template('reports.html', title='Reports & Analytics', active_view='reports', api_endpoint='', view_key='')

@app.route('/projects/new')
def project_new_page():
    return render_template('project_form.html', title='New Project', active_view='projects',
                           api_endpoint='', view_key='', project_id='')

@app.route('/projects/<project_id>/edit')
def project_edit_page(project_id):
    return render_template('project_form.html', title='Edit Project', active_view='projects',
                           api_endpoint='', view_key='', project_id=project_id)

@app.route('/projects/<project_id>')
def project_detail_page(project_id):
    return render_template('project_detail.html', title='Project', active_view='projects',
                           api_endpoint='', view_key='', project_id=project_id)

@app.route('/quotations')
def quotations_page():
    return render_template('quotations.html', title='Quotations', active_view='quotations', api_endpoint='', view_key='')

@app.route('/customers/<customer_id>')
def customer_detail_page(customer_id):
    return render_template('client_360.html', title='Client', active_view='customers',
                           api_endpoint='', view_key='', customer_id=customer_id)

@app.route('/board')
def board_page():
    return render_template('board.html', title='Task Board', active_view='board', api_endpoint='', view_key='')

@app.route('/blog')
def blog_page():
    return render_template('blog.html', title='Blog', active_view='blog', api_endpoint='', view_key='')

@app.route('/enquiries')
def enquiries_page():
    return render_template('enquiries.html', title='Enquiries', active_view='enquiries', api_endpoint='', view_key='')

@app.route('/modules')
def modules_page():
    return render_template('modules.html', title='Modules', active_view='modules', api_endpoint='', view_key='')

@app.route('/users')
def users_page():
    return render_template('users.html', title='System Users', active_view='users', api_endpoint='', view_key='')

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
        'products': {'title': 'Services', 'endpoint': '/products', 'key': 'products'},
        'accounting': {'title': 'Chart of Accounts', 'endpoint': '/accounting/accounts', 'key': 'accounts'},
        'journal_entries': {'title': 'Journal Entries', 'endpoint': '/accounting/journal-entries', 'key': 'entries'},
        'invoices': {'title': 'Invoices', 'endpoint': '/invoices', 'key': 'invoices'},
        'payments': {'title': 'Payments', 'endpoint': '/payments', 'key': 'payments'},
        'expenses': {'title': 'Expenses', 'endpoint': '/expenses', 'key': 'expenses'},
        'hr': {'title': 'Employees', 'endpoint': '/hr', 'key': 'employees'},
        'attendance': {'title': 'Attendance', 'endpoint': '/hr/attendance', 'key': 'attendance'},
        'leaves': {'title': 'Leaves', 'endpoint': '/hr/leaves', 'key': 'leaves'},
        'performance': {'title': 'Performance', 'endpoint': '/hr/performance-reviews', 'key': 'reviews'},
        'time-tracking': {'title': 'Time Tracking', 'endpoint': '/time-tracking', 'key': 'entries'},
        'tickets': {'title': 'Tickets', 'endpoint': '/tickets', 'key': 'tickets'},
        'notifications': {'title': 'Notifications', 'endpoint': '/notifications', 'key': 'notifications'},
        'logs': {'title': 'Logs', 'endpoint': '/logs/system', 'key': 'logs'},
        'settings': {'title': 'Settings', 'endpoint': '/settings', 'key': 'settings'},
    }
    # Note: 'reports' is a dedicated analytics page (see /reports route), not a generic list.

    if view_name in VIEW_CONFIG:
        config = VIEW_CONFIG[view_name]
        return render_template('list_view.html', 
                             title=config['title'], 
                             active_view=view_name, 
                             api_endpoint=config['endpoint'], 
                             view_key=config['key'])
    
    # Special routes are handled by their own dedicated route handlers
    # This prevents this generic handler from returning 404 for them
    if view_name in ['dashboard', 'tools', 'profile', 'settings', 'login', 'register']:
        # Flask should have already matched the specific route, but just in case:
        return redirect(f'/{view_name}')
    
    return "Page not found", 404

# Dedicated Create Page Route
@app.route('/create/<module_name>')
def create_page(module_name):
    VIEW_TITLES = {
        'projects': 'Project', 'tasks': 'Task', 'customers': 'Customer', 'leads': 'Lead',
        'opportunities': 'Opportunity', 'products': 'Service', 'hr': 'Employee', 'invoices': 'Invoice',
        'expenses': 'Expense', 'tickets': 'Support Ticket', 'schedule': 'Event', 'documents': 'Document',
        'sales': 'Sales Order', 'quotations': 'Quotation',
        'accounting': 'Account', 'journal_entries': 'Journal Entry', 'attendance': 'Attendance',
        'leaves': 'Leave Request', 'performance': 'Performance Review', 'users': 'User',
        'time-tracking': 'Time Entry', 'payments': 'Payment', 'notifications': 'Notification', 'reports': 'Report'
    }
    title = VIEW_TITLES.get(module_name, module_name.replace('-', ' ').replace('_', ' ').title())
    return render_template('create.html', title=title, view_name=module_name, active_view=module_name, api_endpoint='', view_key='')

# API Documentation / Health
@app.route('/api')
def api_index():
    return jsonify({
        'message': 'ERP System API',
        'version': '1.0',
        'endpoints': {
            'products': '/api/products',
            'sales': '/api/sales',
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

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    from app.models.auth import TokenBlocklist
    jti = jwt_payload['jti']
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token revoked', 'message': 'Please log in again'}), 401

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', '0') == '1', host='0.0.0.0', port=5000)

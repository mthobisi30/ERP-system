from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from sqlalchemy import func
from app.models.project import Project
from app.models.task import Task
from app.models.sales import SalesOrder
from app.models.customer import Customer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status='active').count()
    total_tasks = Task.query.count()
    pending_tasks = Task.query.filter_by(status='todo').count()
    total_customers = Customer.query.count()
    total_sales = db.session.query(func.sum(SalesOrder.total_amount)).scalar() or 0
    
    return jsonify({
        'projects': {'total': total_projects, 'active': active_projects},
        'tasks': {'total': total_tasks, 'pending': pending_tasks},
        'customers': total_customers,
        'sales': float(total_sales)
    }), 200

@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    return jsonify({
        'projects': [p.to_dict() for p in recent_projects],
        'tasks': [t.to_dict() for t in recent_tasks]
    }), 200

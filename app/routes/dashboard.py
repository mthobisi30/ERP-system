from datetime import date, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from sqlalchemy import func
from app.models.project import Project
from app.models.task import Task
from app.models.customer import Customer
from app.models.schedule import TimeEntry
from app.models.accounting import Invoice
from app.models.retainer import RetainerContract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    open_statuses = ('paid', 'cancelled')

    active_projects = Project.query.filter_by(status='active').count()
    pending_tasks = Task.query.filter_by(status='todo').count()
    total_customers = Customer.query.count()

    billable_hours_week = db.session.query(
        func.coalesce(func.sum(TimeEntry.hours), 0)
    ).filter(TimeEntry.billable.is_(True), TimeEntry.entry_date >= monday).scalar() or 0

    unbilled_amount = db.session.query(
        func.coalesce(func.sum(TimeEntry.hours * TimeEntry.bill_rate), 0)
    ).filter(TimeEntry.billable.is_(True), TimeEntry.invoiced.is_(False),
             TimeEntry.bill_rate.isnot(None)).scalar() or 0

    outstanding_amount = db.session.query(
        func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)
    ).filter(Invoice.status.notin_(open_statuses)).scalar() or 0

    open_invoices = Invoice.query.filter(Invoice.status.notin_(open_statuses)).count()

    mrr = db.session.query(
        func.coalesce(func.sum(RetainerContract.monthly_fee), 0)
    ).filter(RetainerContract.status == 'active').scalar() or 0

    return jsonify({
        'active_projects': active_projects,
        'pending_tasks': pending_tasks,
        'customers': total_customers,
        'billable_hours_week': float(billable_hours_week),
        'unbilled_amount': float(unbilled_amount),
        'outstanding_amount': float(outstanding_amount),
        'open_invoices': open_invoices,
        'mrr': float(mrr),
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

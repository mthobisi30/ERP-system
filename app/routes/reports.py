from datetime import date, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.report import Report
from app.services import reports_service

reports_bp = Blueprint('reports', __name__)


def _parse_date(value, default):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default

@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    reports = Report.query.filter_by(is_active=True).all()
    return jsonify([{'id': str(r.id), 'name': r.name, 'type': r.report_type} for r in reports]), 200

@reports_bp.route('', methods=['POST'])
@jwt_required()
def create_report():
    data = request.get_json()
    report = Report(**data)
    db.session.add(report)
    db.session.commit()
    return jsonify({'id': str(report.id), 'message': 'Report created'}), 201

@reports_bp.route('/utilisation', methods=['GET'])
@reports_bp.route('/utilization', methods=['GET'])
@jwt_required()
def utilisation_report():
    today = date.today()
    d_from = _parse_date(request.args.get('from'), today - timedelta(days=today.weekday()))
    d_to = _parse_date(request.args.get('to'), d_from + timedelta(days=6))
    return jsonify(reports_service.utilisation(d_from, d_to)), 200


@reports_bp.route('/project-profitability', methods=['GET'])
@jwt_required()
def project_profitability_report():
    return jsonify(reports_service.project_profitability()), 200


@reports_bp.route('/pipeline', methods=['GET'])
@jwt_required()
def pipeline_report():
    return jsonify(reports_service.pipeline()), 200


@reports_bp.route('/revenue', methods=['GET'])
@jwt_required()
def revenue_report():
    year = request.args.get('year', date.today().year, type=int)
    return jsonify(reports_service.revenue_by_month(year)), 200


@reports_bp.route('/sales-summary', methods=['GET'])
@jwt_required()
def sales_summary():
    from app.models.sales import SalesOrder
    from sqlalchemy import func
    total_sales = db.session.query(func.sum(SalesOrder.total_amount)).scalar() or 0
    total_orders = SalesOrder.query.count()
    
    return jsonify({
        'total_sales': float(total_sales),
        'total_orders': total_orders,
        'average_order_value': float(total_sales / total_orders) if total_orders > 0 else 0
    }), 200

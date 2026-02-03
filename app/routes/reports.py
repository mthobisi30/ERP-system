from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import db
from app.models.report import Report

reports_bp = Blueprint('reports', __name__)

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

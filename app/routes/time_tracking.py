"""Time Tracking Routes — billable hours, timesheets, approval."""
from datetime import date, datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from config.database import db
from app.models.schedule import TimeEntry
from app.services.billing_service import resolve_bill_rate

time_tracking_bp = Blueprint('time_tracking', __name__)


def _parse_date(value, default=None):
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return default


@time_tracking_bp.route('', methods=['GET'])
@jwt_required()
def get_time_entries():
    """List time entries. Filters: project_id, user_id, from, to, billable, invoiced.

    Defaults to the current user's entries unless an explicit user_id is given.
    """
    q = TimeEntry.query
    user_id = request.args.get('user_id', get_jwt_identity())
    if user_id and user_id != 'all':
        q = q.filter_by(user_id=user_id)

    project_id = request.args.get('project_id')
    if project_id:
        q = q.filter_by(project_id=project_id)

    if request.args.get('billable') is not None:
        q = q.filter(TimeEntry.billable.is_(request.args.get('billable') == 'true'))
    if request.args.get('invoiced') is not None:
        q = q.filter(TimeEntry.invoiced.is_(request.args.get('invoiced') == 'true'))

    d_from = _parse_date(request.args.get('from'))
    d_to = _parse_date(request.args.get('to'))
    if d_from:
        q = q.filter(TimeEntry.entry_date >= d_from)
    if d_to:
        q = q.filter(TimeEntry.entry_date <= d_to)

    entries = q.order_by(TimeEntry.entry_date.desc()).all()
    total_hours = sum(float(e.hours or 0) for e in entries)
    billable_hours = sum(float(e.hours or 0) for e in entries if e.billable)
    return jsonify({
        'entries': [e.to_dict() for e in entries],
        'total_hours': total_hours,
        'billable_hours': billable_hours,
        'billable_amount': sum(e.amount for e in entries),
    }), 200


@time_tracking_bp.route('', methods=['POST'])
@jwt_required()
def create_time_entry():
    """Log time. Auto-resolves the bill rate from the rate chain if not supplied."""
    data = request.get_json() or {}
    if data.get('hours') is None:
        return jsonify({'error': 'hours is required'}), 400

    user_id = get_jwt_identity()
    project_id = data.get('project_id')
    billable = data.get('billable', True)

    bill_rate = data.get('bill_rate')
    if bill_rate is None and billable:
        bill_rate = resolve_bill_rate(user_id, project_id)

    try:
        entry = TimeEntry(
            user_id=user_id,
            project_id=project_id,
            task_id=data.get('task_id'),
            description=data.get('description'),
            entry_date=_parse_date(data.get('entry_date'), date.today()),
            hours=data['hours'],
            billable=billable,
            bill_rate=bill_rate,
            status=data.get('status', 'draft'),
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not create time entry', 'detail': str(exc)}), 400
    return jsonify(entry.to_dict()), 201


@time_tracking_bp.route('/<entry_id>', methods=['GET'])
@jwt_required()
def get_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    return jsonify(entry.to_dict()), 200


@time_tracking_bp.route('/<entry_id>', methods=['PUT'])
@jwt_required()
def update_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.invoiced:
        return jsonify({'error': 'Entry already invoiced and cannot be edited'}), 409

    data = request.get_json() or {}
    allowed = {'description', 'hours', 'billable', 'bill_rate', 'task_id', 'project_id', 'status'}
    for key, value in data.items():
        if key in allowed:
            setattr(entry, key, value)
    if 'entry_date' in data:
        entry.entry_date = _parse_date(data['entry_date'], entry.entry_date)

    try:
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({'error': 'Could not update time entry', 'detail': str(exc)}), 400
    return jsonify(entry.to_dict()), 200


@time_tracking_bp.route('/<entry_id>', methods=['DELETE'])
@jwt_required()
def delete_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.invoiced:
        return jsonify({'error': 'Entry already invoiced and cannot be deleted'}), 409
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Time entry deleted'}), 200


@time_tracking_bp.route('/<entry_id>/submit', methods=['POST'])
@jwt_required()
def submit_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    entry.status = 'submitted'
    db.session.commit()
    return jsonify(entry.to_dict()), 200


@time_tracking_bp.route('/<entry_id>/approve', methods=['POST'])
@jwt_required()
def approve_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    entry.status = 'approved'
    db.session.commit()
    return jsonify(entry.to_dict()), 200


@time_tracking_bp.route('/timesheet', methods=['GET'])
@jwt_required()
def weekly_timesheet():
    """Current user's entries for a week (?week=YYYY-MM-DD, defaults to this week)."""
    anchor = _parse_date(request.args.get('week'), date.today())
    monday = anchor.fromordinal(anchor.toordinal() - anchor.weekday())
    sunday = monday.fromordinal(monday.toordinal() + 6)
    entries = (TimeEntry.query
               .filter(TimeEntry.user_id == get_jwt_identity(),
                       TimeEntry.entry_date >= monday,
                       TimeEntry.entry_date <= sunday)
               .order_by(TimeEntry.entry_date.asc())
               .all())
    by_day = {}
    for e in entries:
        by_day.setdefault(e.entry_date.isoformat(), 0)
        by_day[e.entry_date.isoformat()] += float(e.hours or 0)
    return jsonify({
        'week_start': monday.isoformat(),
        'week_end': sunday.isoformat(),
        'entries': [e.to_dict() for e in entries],
        'hours_by_day': by_day,
        'total_hours': sum(by_day.values()),
    }), 200

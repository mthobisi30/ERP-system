"""Analytics for an agency: utilisation, project profitability, pipeline, revenue.

Profitability uses RateCard.cost_rate to value the cost of logged hours, so
margin = billable-revenue (hours x bill_rate) - cost (hours x cost_rate).
"""
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, case

from config.database import db
from app.models.user import User
from app.models.project import Project
from app.models.rate import RateCard
from app.models.schedule import TimeEntry
from app.models.accounting import Invoice, Expense
from app.models.customer import Opportunity


def _weekdays(d_from, d_to):
    """Count Mon–Fri days in an inclusive date range."""
    if not d_from or not d_to or d_to < d_from:
        return 0
    return sum(1 for i in range((d_to - d_from).days + 1)
               if (d_from + timedelta(days=i)).weekday() < 5)


def build_cost_rate_map():
    """Map of user_id (str) -> cost_rate (Decimal), resolving person then role."""
    users = User.query.all()
    person = {}
    role = {}
    for rc in RateCard.query.filter(RateCard.is_active.is_(True),
                                    RateCard.cost_rate.isnot(None)).all():
        if rc.user_id:
            person.setdefault(str(rc.user_id), rc.cost_rate)
        elif rc.role:
            role.setdefault(rc.role, rc.cost_rate)
    result = {}
    for u in users:
        uid = str(u.id)
        title = u.position or u.role
        result[uid] = person.get(uid) or role.get(title) or Decimal('0')
    return result


def utilisation(d_from, d_to):
    """Per-person billable vs total hours and utilisation against capacity."""
    capacity = _weekdays(d_from, d_to) * 8  # 8h working day
    rows = (db.session.query(
                TimeEntry.user_id,
                func.coalesce(func.sum(TimeEntry.hours), 0),
                func.coalesce(func.sum(case((TimeEntry.billable.is_(True), TimeEntry.hours), else_=0)), 0))
            .filter(TimeEntry.entry_date >= d_from, TimeEntry.entry_date <= d_to)
            .group_by(TimeEntry.user_id).all())

    names = {str(u.id): (f"{u.first_name or ''} {u.last_name or ''}".strip() or u.username)
             for u in User.query.all()}

    people = []
    for user_id, total, billable in rows:
        total, billable = float(total), float(billable)
        people.append({
            'user_id': str(user_id),
            'name': names.get(str(user_id), '—'),
            'total_hours': total,
            'billable_hours': billable,
            'utilisation_of_logged': round(billable / total * 100, 1) if total else 0,
            'utilisation_of_capacity': round(billable / capacity * 100, 1) if capacity else 0,
        })
    people.sort(key=lambda p: p['billable_hours'], reverse=True)
    return {'from': d_from.isoformat(), 'to': d_to.isoformat(),
            'capacity_hours_per_person': capacity, 'people': people}


def project_profitability():
    """Per-project revenue (billable time), cost (all time x cost_rate), margin."""
    cost_map = build_cost_rate_map()
    names = {str(p.id): p.name for p in Project.query.all()}

    # Keyed by str(project_id) so revenue/cost/hours dicts merge correctly.
    revenue = {str(pid): total for pid, total in (db.session.query(
        TimeEntry.project_id,
        func.coalesce(func.sum(TimeEntry.hours * TimeEntry.bill_rate), 0))
        .filter(TimeEntry.billable.is_(True), TimeEntry.bill_rate.isnot(None),
                TimeEntry.project_id.isnot(None))
        .group_by(TimeEntry.project_id).all())}

    cost = {}
    hours = {}
    for project_id, user_id, hrs in (db.session.query(
            TimeEntry.project_id, TimeEntry.user_id, func.coalesce(func.sum(TimeEntry.hours), 0))
            .filter(TimeEntry.project_id.isnot(None))
            .group_by(TimeEntry.project_id, TimeEntry.user_id).all()):
        pid = str(project_id)
        rate = cost_map.get(str(user_id), Decimal('0'))
        cost[pid] = cost.get(pid, Decimal('0')) + Decimal(str(hrs)) * rate
        hours[pid] = hours.get(pid, 0) + float(hrs)

    # Project expenses: all non-rejected expenses add to cost; billable ones are
    # recharged to the client so they also add to revenue (passthrough).
    exp_cost = {str(pid): float(total) for pid, total in (db.session.query(
        Expense.project_id, func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.status != 'rejected', Expense.project_id.isnot(None))
        .group_by(Expense.project_id).all())}
    exp_billable = {str(pid): float(total) for pid, total in (db.session.query(
        Expense.project_id, func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.status != 'rejected', Expense.billable.is_(True),
                Expense.project_id.isnot(None))
        .group_by(Expense.project_id).all())}

    projects = []
    all_ids = set(list(revenue.keys()) + list(cost.keys()) + list(exp_cost.keys()))
    for pid_s in all_ids:
        labour = float(cost.get(pid_s, 0) or 0)
        expenses = float(exp_cost.get(pid_s, 0) or 0)
        rev = float(revenue.get(pid_s, 0) or 0) + float(exp_billable.get(pid_s, 0) or 0)
        cst = labour + expenses
        margin = rev - cst
        projects.append({
            'project_id': pid_s,
            'name': names.get(pid_s, '—'),
            'hours': hours.get(pid_s, 0),
            'revenue': round(rev, 2),
            'labour_cost': round(labour, 2),
            'expenses': round(expenses, 2),
            'cost': round(cst, 2),
            'margin': round(margin, 2),
            'margin_pct': round(margin / rev * 100, 1) if rev else None,
        })
    projects.sort(key=lambda p: p['margin'], reverse=True)
    totals = {
        'revenue': round(sum(p['revenue'] for p in projects), 2),
        'cost': round(sum(p['cost'] for p in projects), 2),
        'margin': round(sum(p['margin'] for p in projects), 2),
    }
    return {'projects': projects, 'totals': totals}


def pipeline():
    """Open opportunities grouped by stage with weighted value."""
    opps = Opportunity.query.filter(Opportunity.status == 'open').all()
    by_stage = {}
    total_value = 0.0
    weighted_total = 0.0
    for o in opps:
        value = float(o.estimated_value or 0)
        weighted = value * (o.probability or 0) / 100
        total_value += value
        weighted_total += weighted
        s = by_stage.setdefault(o.stage or 'unspecified', {'stage': o.stage or 'unspecified',
                                                           'count': 0, 'value': 0.0, 'weighted': 0.0})
        s['count'] += 1
        s['value'] += value
        s['weighted'] += weighted
    return {
        'stages': sorted(by_stage.values(), key=lambda s: s['value'], reverse=True),
        'open_count': len(opps),
        'total_value': round(total_value, 2),
        'weighted_value': round(weighted_total, 2),
    }


def revenue_by_month(year):
    """Invoiced totals per month for a calendar year (excludes cancelled)."""
    rows = (db.session.query(
                func.extract('month', Invoice.invoice_date),
                func.coalesce(func.sum(Invoice.total_amount), 0))
            .filter(func.extract('year', Invoice.invoice_date) == year,
                    Invoice.status != 'cancelled')
            .group_by(func.extract('month', Invoice.invoice_date)).all())
    monthly = {int(m): float(total) for m, total in rows}
    months = [{'month': m, 'total': round(monthly.get(m, 0.0), 2)} for m in range(1, 13)]
    return {'year': year, 'months': months, 'total': round(sum(monthly.values()), 2)}

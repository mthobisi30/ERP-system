"""Expenses tied to projects and folded into profitability."""
from tests.conftest import auth


def _project_with_time(client, mh, dh):
    """Project with 10 billable hours: revenue 10000, labour cost 4000."""
    client.post('/api/rates', headers=mh,
                json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 1000, 'cost_rate': 400})
    pid = client.post('/api/projects', headers=mh,
                      json={'name': 'P', 'status': 'active'}).get_json()['id']
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': pid, 'hours': 10, 'description': 'dev'})
    return pid


def _profit(client, mh, pid):
    data = client.get('/api/reports/project-profitability', headers=mh).get_json()
    return next(p for p in data['projects'] if p['project_id'] == pid)


def test_internal_expense_reduces_margin(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    pid = _project_with_time(client, mh, dh)

    client.post('/api/expenses', headers=mh,
                json={'project_id': pid, 'description': 'Subcontractor', 'amount': 2000, 'billable': False})

    p = _profit(client, mh, pid)
    assert p['revenue'] == 10000
    assert p['labour_cost'] == 4000
    assert p['expenses'] == 2000
    assert p['cost'] == 6000
    assert p['margin'] == 4000  # 6000 margin reduced by the 2000 internal expense


def test_billable_expense_is_passthrough(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    pid = _project_with_time(client, mh, dh)

    client.post('/api/expenses', headers=mh,
                json={'project_id': pid, 'description': 'Stock images', 'amount': 1000, 'billable': True})

    p = _profit(client, mh, pid)
    assert p['revenue'] == 11000   # 10000 time + 1000 recharged
    assert p['cost'] == 5000       # 4000 labour + 1000 expense
    assert p['margin'] == 6000     # passthrough: margin unchanged


def test_rejected_expense_excluded(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    pid = _project_with_time(client, mh, dh)
    exp = client.post('/api/expenses', headers=mh,
                      json={'project_id': pid, 'description': 'Bad', 'amount': 5000}).get_json()
    client.post(f'/api/expenses/{exp["id"]}/approve', headers=mh, json={'decision': 'rejected'})
    p = _profit(client, mh, pid)
    assert p['expenses'] == 0  # rejected expense doesn't count


def test_expense_filter_and_employee_cannot_approve(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    eh = auth(make_user(role='employee')['token'])
    pid = client.post('/api/projects', headers=mh, json={'name': 'P'}).get_json()['id']
    exp = client.post('/api/expenses', headers=eh,
                      json={'project_id': pid, 'description': 'Taxi', 'amount': 150}).get_json()

    listed = client.get(f'/api/expenses?project_id={pid}', headers=mh).get_json()
    assert listed['total'] == 1

    # employees can log expenses but not approve them
    r = client.post(f'/api/expenses/{exp["id"]}/approve', headers=eh, json={})
    assert r.status_code == 403

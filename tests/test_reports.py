"""Analytics reports tests."""
from tests.conftest import auth


def _setup_time(client, mh, dh, bill=1000, cost=400, billable_h=8, nonbillable_h=2):
    """Create a Developer rate card, a project, and log time. Returns project id."""
    client.post('/api/rates', headers=mh,
                json={'name': 'Developer', 'role': 'Developer', 'bill_rate': bill, 'cost_rate': cost})
    proj = client.post('/api/projects', headers=mh,
                       json={'name': 'P', 'status': 'active', 'billing_type': 'time_and_materials'}).get_json()
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': proj['id'], 'hours': billable_h, 'description': 'build'})
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': proj['id'], 'hours': nonbillable_h, 'description': 'standup', 'billable': False})
    return proj['id']


def test_utilisation(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    _setup_time(client, mh, dh)
    data = client.get('/api/reports/utilisation', headers=mh).get_json()
    me = [p for p in data['people'] if p['billable_hours'] == 8]
    assert me, data
    assert me[0]['total_hours'] == 10
    assert me[0]['utilisation_of_logged'] == 80.0  # 8 / 10


def test_project_profitability_margin(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    _setup_time(client, mh, dh)  # 8 billable @1000 = 8000 revenue; 10h @400 = 4000 cost
    data = client.get('/api/reports/project-profitability', headers=mh).get_json()
    p = data['projects'][0]
    assert p['revenue'] == 8000
    assert p['cost'] == 4000
    assert p['margin'] == 4000
    assert p['margin_pct'] == 50.0
    assert data['totals']['margin'] == 4000


def test_pipeline(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    client.post('/api/opportunities', headers=mh,
                json={'name': 'Big deal', 'estimated_value': 100000, 'stage': 'proposal', 'probability': 50})
    data = client.get('/api/reports/pipeline', headers=mh).get_json()
    assert data['open_count'] == 1
    assert data['total_value'] == 100000
    assert data['weighted_value'] == 50000  # 100000 * 50%


def test_revenue_by_month(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    pid = _setup_time(client, mh, dh)
    # Invoice the billable time: 8000 + 15% VAT = 9200, dated today (this year).
    client.post('/api/invoices/generate-from-time', headers=mh, json={'project_id': pid})
    data = client.get('/api/reports/revenue', headers=mh).get_json()
    assert data['total'] == 9200
    assert sum(m['total'] for m in data['months']) == 9200

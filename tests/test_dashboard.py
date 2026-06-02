"""Dashboard stats endpoint (exercises the aggregate SQL)."""
from tests.conftest import auth


def test_dashboard_stats_shape_and_aggregates(client, make_user):
    mgr = make_user(role='manager')
    dev = make_user(role='employee', position='Developer')
    mh, dh = auth(mgr['token']), auth(dev['token'])

    # Empty dashboard works and returns all keys.
    r = client.get('/api/dashboard/stats', headers=mh)
    assert r.status_code == 200
    body = r.get_json()
    for key in ('active_projects', 'billable_hours_week', 'unbilled_amount',
                'outstanding_amount', 'open_invoices', 'pending_tasks', 'customers'):
        assert key in body, key
    assert body['unbilled_amount'] == 0

    # Create a project + rate + log billable time -> unbilled value reflects it.
    client.post('/api/rates', headers=mh,
                json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 1000})
    proj = client.post('/api/projects', headers=mh,
                       json={'name': 'P', 'status': 'active', 'billing_type': 'time_and_materials'}).get_json()
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': proj['id'], 'hours': 5, 'description': 'work'})

    body = client.get('/api/dashboard/stats', headers=mh).get_json()
    assert body['active_projects'] == 1
    assert body['billable_hours_week'] == 5
    assert body['unbilled_amount'] == 5000  # 5h * R1000

    # After invoicing, unbilled drops to 0 and outstanding rises.
    client.post('/api/invoices/generate-from-time', headers=mh, json={'project_id': proj['id']})
    body = client.get('/api/dashboard/stats', headers=mh).get_json()
    assert body['unbilled_amount'] == 0
    assert body['open_invoices'] == 1
    assert body['outstanding_amount'] == 5750  # 5000 + 15% VAT

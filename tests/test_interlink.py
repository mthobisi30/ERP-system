"""Interconnection: tickets ↔ project/client, project filtering by client."""
from tests.conftest import auth


def test_ticket_autonumber_and_links(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cust = client.post('/api/customers', headers=h, json={'company_name': 'Acme'}).get_json()
    proj = client.post('/api/projects', headers=h, json={'name': 'P', 'customer_id': cust['id']}).get_json()

    t = client.post('/api/tickets', headers=h, json={
        'subject': 'Login broken', 'priority': 'high',
        'project_id': proj['id'], 'customer_id': cust['id']})
    assert t.status_code == 201
    body = t.get_json()
    assert body['ticket_number'] == 'TKT-00001'
    assert body['project_id'] == proj['id'] and body['customer_id'] == cust['id']

    by_proj = client.get(f"/api/tickets?project_id={proj['id']}", headers=h).get_json()
    assert by_proj['total'] == 1 and by_proj['open_count'] == 1
    by_cust = client.get(f"/api/tickets?customer_id={cust['id']}", headers=h).get_json()
    assert by_cust['total'] == 1


def test_projects_filter_by_customer(client, make_user):
    h = auth(make_user(role='manager')['token'])
    a = client.post('/api/customers', headers=h, json={'company_name': 'Alpha'}).get_json()
    b = client.post('/api/customers', headers=h, json={'company_name': 'Beta'}).get_json()
    client.post('/api/projects', headers=h, json={'name': 'A1', 'customer_id': a['id']})
    client.post('/api/projects', headers=h, json={'name': 'A2', 'customer_id': a['id']})
    client.post('/api/projects', headers=h, json={'name': 'B1', 'customer_id': b['id']})

    res = client.get(f"/api/projects?customer_id={a['id']}", headers=h).get_json()
    assert res['total'] == 2
    assert all(p['customer_id'] == a['id'] for p in res['projects'])


def test_ticket_resolved_not_counted_open(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cust = client.post('/api/customers', headers=h, json={'company_name': 'Acme'}).get_json()
    t = client.post('/api/tickets', headers=h, json={'subject': 'x', 'customer_id': cust['id']}).get_json()
    client.put(f"/api/tickets/{t['id']}", headers=h, json={'status': 'resolved'})
    data = client.get(f"/api/tickets?customer_id={cust['id']}", headers=h).get_json()
    assert data['total'] == 1 and data['open_count'] == 0

"""SDLC activity trail / audit."""
from tests.conftest import auth


def test_project_and_client_activity_trail(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cust = client.post('/api/customers', headers=h, json={'company_name': 'Acme'}).get_json()
    proj = client.post('/api/projects', headers=h, json={'name': 'P', 'customer_id': cust['id']}).get_json()

    act = client.get(f"/api/projects/{proj['id']}/activity", headers=h).get_json()['activity']
    assert any(a['action'] == 'project.created' for a in act)

    client.post('/api/tickets', headers=h, json={'subject': 'Bug', 'project_id': proj['id'], 'customer_id': cust['id']})
    act = client.get(f"/api/projects/{proj['id']}/activity", headers=h).get_json()['activity']
    assert any(a['action'] == 'ticket.created' for a in act)

    # client-scoped trail aggregates project + ticket events
    cact = client.get(f"/api/customers/{cust['id']}/activity", headers=h).get_json()['activity']
    assert len(cact) >= 2
    assert all(a['customer_id'] == cust['id'] for a in cact)


def test_invoice_generation_is_logged(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    client.post('/api/rates', headers=mh, json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 1000})
    cust = client.post('/api/customers', headers=mh, json={'company_name': 'Acme'}).get_json()
    proj = client.post('/api/projects', headers=mh, json={'name': 'P', 'customer_id': cust['id']}).get_json()
    client.post('/api/time-tracking', headers=dh, json={'project_id': proj['id'], 'hours': 4, 'description': 'w'})
    client.post('/api/invoices/generate-from-time', headers=mh, json={'project_id': proj['id']})

    act = client.get(f"/api/projects/{proj['id']}/activity", headers=mh).get_json()['activity']
    actions = {a['action'] for a in act}
    assert 'invoice.generated' in actions

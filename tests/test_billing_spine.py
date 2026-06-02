"""End-to-end tests for the agency spine: lead -> project -> time -> invoice."""
from tests.conftest import auth


def test_full_spine(client, make_user):
    manager = make_user(role='manager')
    developer = make_user(role='employee', position='Developer')
    mh = auth(manager['token'])
    dh = auth(developer['token'])

    # Rate card for the "Developer" band @ R800/h
    r = client.post('/api/rates', headers=mh,
                    json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 800, 'cost_rate': 350})
    assert r.status_code == 201, r.get_json()

    # Customer
    cust = client.post('/api/customers', headers=mh,
                       json={'company_name': 'Acme', 'email': 'acme@acme.co.za'}).get_json()
    cid = cust['id']

    # Opportunity -> convert to project
    opp = client.post('/api/opportunities', headers=mh,
                      json={'name': 'Build', 'customer_id': cid, 'estimated_value': 100000}).get_json()
    conv = client.post(f'/api/opportunities/{opp["id"]}/convert-to-project', headers=mh,
                       json={'billing_type': 'time_and_materials'})
    assert conv.status_code == 201
    project = conv.get_json()['project']
    pid = project['id']
    assert project['customer_id'] == cid
    assert project['opportunity_id'] == opp['id']

    # Developer logs 8 billable hours; rate auto-resolves from the Developer rate card
    t = client.post('/api/time-tracking', headers=dh,
                    json={'project_id': pid, 'hours': 8, 'description': 'Coding'})
    assert t.status_code == 201
    assert t.get_json()['bill_rate'] == 800
    assert t.get_json()['amount'] == 6400

    # ...and 2 non-billable hours (must be excluded)
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': pid, 'hours': 2, 'description': 'Standup', 'billable': False})

    # Unbilled summary
    un = client.get(f'/api/projects/{pid}/unbilled-time', headers=mh).get_json()
    assert un['total_hours'] == 8
    assert un['total_amount'] == 6400

    # Generate invoice (ZAR + 15% VAT): 6400 + 960 = 7360
    gen = client.post('/api/invoices/generate-from-time', headers=mh, json={'project_id': pid})
    assert gen.status_code == 201
    inv = gen.get_json()['invoice']
    assert inv['subtotal'] == 6400
    assert inv['vat_amount'] == 960
    assert inv['total_amount'] == 7360
    assert inv['currency'] == 'ZAR'
    assert len(gen.get_json()['items']) == 1

    # Idempotent: nothing left to bill
    assert client.post('/api/invoices/generate-from-time', headers=mh,
                       json={'project_id': pid}).status_code == 400

    # Pay it: partial then full
    p1 = client.post('/api/payments', headers=mh,
                     json={'invoice_id': inv['id'], 'amount': 3360, 'payment_method': 'eft'})
    assert p1.get_json()['invoice']['status'] == 'partial'
    p2 = client.post('/api/payments', headers=mh,
                     json={'invoice_id': inv['id'], 'amount': 4000, 'payment_method': 'eft'})
    assert p2.get_json()['invoice']['status'] == 'paid'
    assert p2.get_json()['invoice']['balance_due'] == 0


def test_employee_cannot_create_rate_card(client, make_user):
    emp = make_user(role='employee')
    r = client.post('/api/rates', headers=auth(emp['token']),
                    json={'name': 'x', 'bill_rate': 500})
    assert r.status_code == 403


def test_time_entry_locked_after_invoicing(client, make_user):
    mgr = make_user(role='manager')
    dev = make_user(role='employee', position='Developer')
    client.post('/api/rates', headers=auth(mgr['token']),
                json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 800})
    proj = client.post('/api/projects', headers=auth(mgr['token']),
                       json={'name': 'P', 'billing_type': 'time_and_materials'}).get_json()
    entry = client.post('/api/time-tracking', headers=auth(dev['token']),
                        json={'project_id': proj['id'], 'hours': 4, 'description': 'work'}).get_json()
    client.post('/api/invoices/generate-from-time', headers=auth(mgr['token']),
                json={'project_id': proj['id']})
    # editing an invoiced entry is rejected
    r = client.put(f'/api/time-tracking/{entry["id"]}', headers=auth(dev['token']),
                   json={'hours': 99})
    assert r.status_code == 409

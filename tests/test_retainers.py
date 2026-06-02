"""Retainer / recurring-billing tests."""
from tests.conftest import auth


def _customer(client, mh):
    return client.post('/api/customers', headers=mh,
                       json={'company_name': 'Acme', 'email': 'acme@acme.co.za'}).get_json()['id']


def test_create_list_and_mrr(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    cid = _customer(client, mh)
    r = client.post('/api/retainers', headers=mh,
                    json={'name': 'Acme Support', 'customer_id': cid, 'monthly_fee': 5000})
    assert r.status_code == 201

    body = client.get('/api/retainers', headers=mh).get_json()
    assert body['total'] == 1
    assert body['mrr'] == 5000  # one active contract


def test_employee_cannot_create_retainer(client, make_user):
    eh = auth(make_user(role='employee')['token'])
    mh = auth(make_user(role='manager')['token'])
    cid = _customer(client, mh)
    r = client.post('/api/retainers', headers=eh,
                    json={'name': 'X', 'customer_id': cid, 'monthly_fee': 100})
    assert r.status_code == 403


def test_run_retainers_creates_invoice_and_is_idempotent(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    cid = _customer(client, mh)
    client.post('/api/retainers', headers=mh,
                json={'name': 'Acme Support', 'customer_id': cid, 'monthly_fee': 5000})

    # First run creates one invoice: 5000 + 15% VAT = 5750
    run1 = client.post('/api/retainers/run', headers=mh, json={}).get_json()
    assert run1['created_count'] == 1
    inv = run1['invoices'][0]
    assert inv['subtotal'] == 5000
    assert inv['vat_amount'] == 750
    assert inv['total_amount'] == 5750

    # Second run for the same period is idempotent — nothing new created
    run2 = client.post('/api/retainers/run', headers=mh, json={}).get_json()
    assert run2['created_count'] == 0
    assert run2['skipped_count'] == 1


def test_run_retainers_no_vat_when_disabled_on_contract(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    cid = _customer(client, mh)
    client.post('/api/retainers', headers=mh,
                json={'name': 'No VAT', 'customer_id': cid, 'monthly_fee': 1000, 'vat_applicable': False})
    inv = client.post('/api/retainers/run', headers=mh, json={}).get_json()['invoices'][0]
    assert inv['vat_amount'] == 0
    assert inv['total_amount'] == 1000


def test_dashboard_includes_mrr(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    cid = _customer(client, mh)
    client.post('/api/retainers', headers=mh,
                json={'name': 'Acme Support', 'customer_id': cid, 'monthly_fee': 8000})
    body = client.get('/api/dashboard/stats', headers=mh).get_json()
    assert body['mrr'] == 8000

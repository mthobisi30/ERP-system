"""Emailing generated PDFs (suppressed in tests via MAIL_SUPPRESS_SEND)."""
from tests.conftest import auth


def test_send_invoice_endpoint_works_and_degrades_gracefully(client, make_user):
    """With a recipient, the endpoint builds the PDF and attempts delivery; with mail
    unconfigured (as in CI) it returns 200 sent:false rather than erroring."""
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    client.post('/api/rates', headers=mh, json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 1000})
    cust = client.post('/api/customers', headers=mh, json={'company_name': 'Acme', 'email': 'acme@x.co.za'}).get_json()
    proj = client.post('/api/projects', headers=mh, json={'name': 'P', 'customer_id': cust['id']}).get_json()
    client.post('/api/time-tracking', headers=dh, json={'project_id': proj['id'], 'hours': 4, 'description': 'w'})
    inv = client.post('/api/invoices/generate-from-time', headers=mh, json={'project_id': proj['id']}).get_json()['invoice']

    r = client.post(f"/api/invoices/{inv['id']}/send", headers=mh, json={})
    assert r.status_code == 200
    assert r.get_json()['sent'] is False  # mail not configured in tests → graceful, not an error


def test_send_invoice_without_recipient_rejected(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    inv = client.post('/api/invoices', headers=mh, json={'subtotal': 100}).get_json()  # no client/email
    r = client.post(f"/api/invoices/{inv['id']}/send", headers=mh, json={})
    assert r.status_code == 400

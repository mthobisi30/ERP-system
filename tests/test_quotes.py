"""Quote / proposal funnel tests."""
from tests.conftest import auth


def _customer(client, h):
    return client.post('/api/customers', headers=h,
                       json={'company_name': 'Acme', 'email': 'a@acme.co.za'}).get_json()['id']


def test_create_quote_computes_vat(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cid = _customer(client, h)
    r = client.post('/api/sales/quotations', headers=h, json={
        'title': 'Build', 'customer_id': cid,
        'items': [{'description': 'Dev', 'quantity': 2, 'unit_price': 5000}],
    })
    assert r.status_code == 201, r.get_json()
    q = r.get_json()
    assert q['subtotal'] == 10000
    assert q['tax_amount'] == 1500      # 15% VAT
    assert q['total_amount'] == 11500
    assert q['status'] == 'draft'
    assert q['quote_number'].startswith('Q-')

    # items are persisted and returned on detail
    detail = client.get(f'/api/sales/quotations/{q["id"]}', headers=h).get_json()
    assert len(detail['items']) == 1
    assert detail['items'][0]['line_total'] == 10000


def test_send_then_accept_creates_project(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cid = _customer(client, h)
    q = client.post('/api/sales/quotations', headers=h, json={
        'title': 'Platform', 'customer_id': cid,
        'items': [{'description': 'Work', 'quantity': 1, 'unit_price': 20000}],
    }).get_json()

    sent = client.post(f'/api/sales/quotations/{q["id"]}/status', headers=h, json={'status': 'sent'})
    assert sent.get_json()['status'] == 'sent'

    acc = client.post(f'/api/sales/quotations/{q["id"]}/accept', headers=h, json={})
    assert acc.status_code == 201
    body = acc.get_json()
    assert body['quote']['status'] == 'accepted'
    assert body['project']['customer_id'] == cid
    assert body['project']['billing_type'] == 'fixed_price'
    assert body['project']['budget'] == 23000  # 20000 + 15% VAT
    assert body['quote']['converted_project_id'] == body['project']['id']

    # Accepting again is rejected
    again = client.post(f'/api/sales/quotations/{q["id"]}/accept', headers=h, json={})
    assert again.status_code == 409


def test_decline_quote(client, make_user):
    h = auth(make_user(role='manager')['token'])
    q = client.post('/api/sales/quotations', headers=h, json={
        'title': 'X', 'items': [{'description': 'a', 'quantity': 1, 'unit_price': 100}]}).get_json()
    r = client.post(f'/api/sales/quotations/{q["id"]}/status', headers=h, json={'status': 'declined'})
    assert r.get_json()['status'] == 'declined'

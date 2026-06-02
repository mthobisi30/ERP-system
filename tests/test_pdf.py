"""PDF generation for invoices and quotes."""
from tests.conftest import auth


def test_invoice_pdf(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    dh = auth(make_user(role='employee', position='Developer')['token'])
    client.post('/api/rates', headers=mh,
                json={'name': 'Developer', 'role': 'Developer', 'bill_rate': 1000})
    pid = client.post('/api/projects', headers=mh, json={'name': 'P'}).get_json()['id']
    client.post('/api/time-tracking', headers=dh,
                json={'project_id': pid, 'hours': 4, 'description': 'work'})
    inv = client.post('/api/invoices/generate-from-time', headers=mh,
                      json={'project_id': pid}).get_json()['invoice']

    r = client.get(f'/api/invoices/{inv["id"]}/pdf', headers=mh)
    assert r.status_code == 200
    assert r.content_type.startswith('application/pdf')
    assert r.data[:4] == b'%PDF'
    assert len(r.data) > 1000  # a real document, not an empty stub


def test_quote_pdf(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    q = client.post('/api/sales/quotations', headers=mh, json={
        'title': 'Build', 'items': [{'description': 'Dev', 'quantity': 2, 'unit_price': 5000}],
    }).get_json()
    r = client.get(f'/api/sales/quotations/{q["id"]}/pdf', headers=mh)
    assert r.status_code == 200
    assert r.content_type.startswith('application/pdf')
    assert r.data[:4] == b'%PDF'


def test_invoice_pdf_404(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    r = client.get('/api/invoices/00000000-0000-0000-0000-000000000000/pdf', headers=mh)
    assert r.status_code == 404

"""Document engine: issuer settings, payment schedule, phases, generated PDFs."""
from tests.conftest import auth


def _project(client, mh):
    cust = client.post('/api/customers', headers=mh,
                       json={'company_name': 'MPIA Services (PTY) Ltd', 'contact_person': 'Mpilo Mhlongo',
                             'email': 'info@mpiaserv.co.za'}).get_json()
    return client.post('/api/projects', headers=mh, json={
        'name': 'ILMS', 'customer_id': cust['id'],
        'system_name': 'Inspection Lifecycle Management System (ILMS)',
        'contract_ref': 'MPIA-BRD-002 v2.0', 'contract_value': 19000}).get_json()


def test_issuer_settings_roundtrip(client, make_user):
    ah = auth(make_user(role='admin')['token'])
    r = client.put('/api/settings', headers=ah, json={
        'company_name': 'Rephina Software Solutions',
        'legal_name': 'Rephina Software Solutions (PTY) LTD',
        'registration_number': '2026/250285/07', 'signatory_name': 'Mthobisi Nxumalo',
        'bank_name': 'Capitec', 'bank_account_number': '2474407789', 'doc_ref_prefix': 'RSS'})
    assert r.status_code == 200
    s = client.get('/api/settings', headers=ah).get_json()
    assert s['legal_name'] == 'Rephina Software Solutions (PTY) LTD'
    assert s['registration_number'] == '2026/250285/07'
    assert s['bank_name'] == 'Capitec'


def test_payment_schedule(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    p = _project(client, mh)
    r = client.post(f"/api/projects/{p['id']}/milestones", headers=mh, json={
        'name': 'Milestone 1', 'trigger': 'Phase 1 gate acceptance', 'amount': 3500,
        'invoice_ref': 'RSS-INV-2026-003', 'payment_status': 'pending'})
    assert r.status_code == 201
    assert r.get_json()['amount'] == 3500
    rows = client.get(f"/api/projects/{p['id']}/milestones", headers=mh).get_json()
    assert len(rows) == 1 and rows[0]['payment_status'] == 'pending'


def test_phase_and_milestone_report_pdf(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    p = _project(client, mh)
    ph = client.post(f"/api/projects/{p['id']}/phases", headers=mh, json={
        'number': 2, 'total_phases': 4, 'title': 'Mobile Data Capture, Offline Engine & Geospatial',
        'phase_value': 3000, 'triggers_invoice_ref': 'RSS-INV-2026-004',
        'gate_status': 'Met and exceeded', 'gate_criteria': 'A technician completes 20 joint records offline.'}).get_json()
    client.post(f"/api/projects/phases/{ph['id']}/deliverables", headers=mh, json={
        'name': 'Mobile app — joint entry', 'implementation': 'Flutter app', 'status': 'Complete'})
    # deliverable shows in phase listing
    phases = client.get(f"/api/projects/{p['id']}/phases", headers=mh).get_json()['phases']
    assert len(phases[0]['deliverables']) == 1

    r = client.get(f"/api/projects/phases/{ph['id']}/report.pdf", headers=mh)
    assert r.status_code == 200
    assert r.content_type.startswith('application/pdf')
    assert r.data[:4] == b'%PDF'


def test_endorsement_doc_numbering_and_pdf(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    p = _project(client, mh)
    e1 = client.post(f"/api/projects/{p['id']}/documents", headers=mh, json={
        'doc_type': 'END', 'title': 'Goodwill Discount Endorsement',
        'data': {'original_value': 19000, 'discount': 1500, 'revised_value': 17500,
                 'delay_period': '31 Mar – 23 Apr 2026', 'reason': 'Personal circumstances',
                 'purpose': 'Records a goodwill discount.'}}).get_json()
    assert e1['doc_ref'].startswith('RSS-END-') and e1['doc_ref'].endswith('-001')
    e2 = client.post(f"/api/projects/{p['id']}/documents", headers=mh,
                     json={'doc_type': 'END', 'data': {}}).get_json()
    assert e2['doc_ref'].endswith('-002')  # auto-incrementing per type/year

    r = client.get(f"/api/projects/documents/{e1['id']}/pdf", headers=mh)
    assert r.status_code == 200 and r.content_type.startswith('application/pdf') and r.data[:4] == b'%PDF'


def test_migration_notice_pdf(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    p = _project(client, mh)
    # a payment line so the carried-forward schedule renders
    client.post(f"/api/projects/{p['id']}/milestones", headers=mh,
                json={'name': 'Deposit', 'amount': 3600, 'payment_status': 'paid'})
    doc = client.post(f"/api/projects/{p['id']}/documents", headers=mh, json={
        'doc_type': 'PMN', 'title': 'Project Migration Notice',
        'data': {'notice': 'Codebase retired and rebuilt.', 'retired': ['mpia-nexus'],
                 'replacement': ['mpia-serv-admin'], 'reasons': [{'issue': 'Blank app', 'severity': 'Critical'}]}}).get_json()
    assert doc['doc_ref'].startswith('RSS-PMN-')
    r = client.get(f"/api/projects/documents/{doc['id']}/pdf", headers=mh)
    assert r.status_code == 200 and r.data[:4] == b'%PDF'


def test_bad_doc_type_rejected(client, make_user):
    mh = auth(make_user(role='manager')['token'])
    p = _project(client, mh)
    r = client.post(f"/api/projects/{p['id']}/documents", headers=mh, json={'doc_type': 'XXX', 'data': {}})
    assert r.status_code == 400

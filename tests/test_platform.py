"""Tests for the new modules: blog, enquiries, module config, admin users."""
from tests.conftest import auth


# ---------- Blog ----------

def test_blog_create_publish_and_public_visibility(client, make_user):
    h = auth(make_user(role='manager')['token'])
    created = client.post('/api/blog', headers=h, json={
        'title': 'Hello World', 'excerpt': 'hi', 'body': 'Full body', 'tags': 'a, b'}).get_json()
    assert created['slug'] == 'hello-world'
    assert created['status'] == 'draft'

    # draft is not public
    assert client.get('/api/public/blog').get_json()['posts'] == []
    assert client.get('/api/public/blog/hello-world').status_code == 404

    # publish → public
    client.post(f'/api/blog/{created["id"]}/publish', headers=h, json={'publish': True})
    pub = client.get('/api/public/blog').get_json()['posts']
    assert len(pub) == 1 and pub[0]['slug'] == 'hello-world'
    full = client.get('/api/public/blog/hello-world').get_json()
    assert full['body'] == 'Full body'  # full=True includes body


def test_blog_slug_uniqueness(client, make_user):
    h = auth(make_user(role='manager')['token'])
    a = client.post('/api/blog', headers=h, json={'title': 'Same Title'}).get_json()
    b = client.post('/api/blog', headers=h, json={'title': 'Same Title'}).get_json()
    assert a['slug'] != b['slug']  # second gets -2 suffix


# ---------- Enquiries ----------

def test_public_enquiry_submit_and_internal_view(client, make_user):
    # public submit needs no auth
    r = client.post('/api/public/enquiries', json={
        'name': 'Jane', 'email': 'jane@x.co.za', 'message': 'Need a website'})
    assert r.status_code == 201

    h = auth(make_user(role='employee')['token'])
    data = client.get('/api/enquiries', headers=h).get_json()
    assert data['total'] == 1
    assert data['new_count'] == 1
    eid = data['enquiries'][0]['id']

    client.put(f'/api/enquiries/{eid}', headers=h, json={'status': 'responded'})
    assert client.get('/api/enquiries', headers=h).get_json()['new_count'] == 0


def test_public_enquiry_requires_fields(client):
    assert client.post('/api/public/enquiries', json={'name': 'X'}).status_code == 400


# ---------- Module config ----------

def test_modules_seed_and_toggle(client, make_user):
    ah = auth(make_user(role='admin')['token'])
    data = client.get('/api/modules', headers=ah).get_json()
    assert len(data['modules']) > 10
    assert 'blog' in data['enabled']

    # disable a non-core module
    client.put('/api/modules/blog', headers=ah, json={'enabled': False})
    assert 'blog' not in client.get('/api/modules/enabled', headers=ah).get_json()['enabled']

    # core cannot be disabled
    assert client.put('/api/modules/dashboard', headers=ah, json={'enabled': False}).status_code == 400


def test_modules_toggle_requires_admin(client, make_user):
    eh = auth(make_user(role='employee')['token'])
    client.get('/api/modules', headers=eh)  # seed
    assert client.put('/api/modules/blog', headers=eh, json={'enabled': False}).status_code == 403


# ---------- Admin users ----------

def test_admin_creates_user(client, make_user):
    ah = auth(make_user(role='admin')['token'])
    r = client.post('/api/users', headers=ah, json={
        'email': 'new@rephina.co.za', 'username': 'newbie', 'password': 'Password123', 'role': 'manager'})
    assert r.status_code == 201
    assert r.get_json()['role'] == 'manager'
    # duplicate email rejected
    assert client.post('/api/users', headers=ah, json={
        'email': 'new@rephina.co.za', 'username': 'x', 'password': 'Password123'}).status_code == 400


def test_employee_cannot_create_user(client, make_user):
    eh = auth(make_user(role='employee')['token'])
    r = client.post('/api/users', headers=eh, json={
        'email': 'z@z.co.za', 'username': 'z', 'password': 'Password123'})
    assert r.status_code == 403

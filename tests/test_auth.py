"""Auth + authorization tests."""
from tests.conftest import auth


def test_register_then_login(client):
    r = client.post('/api/auth/register', json={
        'email': 'new@test.co.za', 'username': 'newbie', 'password': 'Password123',
    })
    assert r.status_code == 201, r.get_json()

    r = client.post('/api/auth/login', json={'email': 'new@test.co.za', 'password': 'Password123'})
    body = r.get_json()
    assert r.status_code == 200
    assert body['access_token'] and body['refresh_token']


def test_register_cannot_grant_admin(client):
    """Self-registration must never set an elevated role."""
    client.post('/api/auth/register', json={
        'email': 'sneaky@test.co.za', 'username': 'sneaky',
        'password': 'Password123', 'role': 'admin',
    })
    r = client.post('/api/auth/login', json={'email': 'sneaky@test.co.za', 'password': 'Password123'})
    assert r.get_json()['user']['role'] == 'employee'


def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'email': 'a@test.co.za', 'username': 'a', 'password': 'Password123'})
    r = client.post('/api/auth/login', json={'email': 'a@test.co.za', 'password': 'wrong'})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get('/api/auth/me').status_code == 401


def test_refresh_issues_new_access_token(client):
    client.post('/api/auth/register', json={
        'email': 'r@test.co.za', 'username': 'r', 'password': 'Password123'})
    tokens = client.post('/api/auth/login', json={
        'email': 'r@test.co.za', 'password': 'Password123'}).get_json()
    r = client.post('/api/auth/refresh', headers=auth(tokens['refresh_token']))
    assert r.status_code == 200 and r.get_json()['access_token']


def test_logout_revokes_token(client):
    client.post('/api/auth/register', json={
        'email': 'l@test.co.za', 'username': 'l', 'password': 'Password123'})
    token = client.post('/api/auth/login', json={
        'email': 'l@test.co.za', 'password': 'Password123'}).get_json()['access_token']
    assert client.get('/api/auth/me', headers=auth(token)).status_code == 200
    assert client.post('/api/auth/logout', headers=auth(token)).status_code == 200
    # token is now revoked
    assert client.get('/api/auth/me', headers=auth(token)).status_code == 401


def test_change_password(client):
    client.post('/api/auth/register', json={
        'email': 'c@test.co.za', 'username': 'c', 'password': 'Password123'})
    token = client.post('/api/auth/login', json={
        'email': 'c@test.co.za', 'password': 'Password123'}).get_json()['access_token']
    r = client.post('/api/auth/change-password', headers=auth(token),
                    json={'current_password': 'Password123', 'new_password': 'Brandnew123'})
    assert r.status_code == 200
    assert client.post('/api/auth/login', json={
        'email': 'c@test.co.za', 'password': 'Brandnew123'}).status_code == 200


def test_employee_cannot_list_users(client, make_user):
    emp = make_user(role='employee')
    assert client.get('/api/users', headers=auth(emp['token'])).status_code == 403


def test_manager_can_list_users(client, make_user):
    mgr = make_user(role='manager')
    assert client.get('/api/users', headers=auth(mgr['token'])).status_code == 200


def test_employee_cannot_delete_user(client, make_user):
    emp = make_user(role='employee')
    victim = make_user(role='employee')
    assert client.delete(f'/api/users/{victim["id"]}', headers=auth(emp['token'])).status_code == 403


def test_non_admin_cannot_escalate_role(client, make_user):
    """A user editing their own profile cannot promote themselves to admin."""
    emp = make_user(role='employee')
    r = client.put(f'/api/users/{emp["id"]}', headers=auth(emp['token']),
                   json={'role': 'admin', 'first_name': 'Eve'})
    assert r.status_code == 200
    assert r.get_json()['role'] == 'employee'  # role change ignored
    assert r.get_json()['first_name'] == 'Eve'  # allowed change applied

"""Global cross-entity search."""
from tests.conftest import auth


def test_global_search_matches_client_and_project(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cust = client.post('/api/customers', headers=h, json={'company_name': 'Acme Industries'}).get_json()
    client.post('/api/projects', headers=h, json={'name': 'Acme Portal', 'customer_id': cust['id']})

    r = client.get('/api/search?q=Acme', headers=h).get_json()
    types = {x['type'] for x in r['results']}
    assert 'Client' in types and 'Project' in types
    assert any('/customers/' in x['url'] for x in r['results'])


def test_search_requires_two_chars(client, make_user):
    h = auth(make_user(role='manager')['token'])
    assert client.get('/api/search?q=a', headers=h).get_json()['results'] == []

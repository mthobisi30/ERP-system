"""Public developer showcase (case studies)."""
from tests.conftest import auth


def test_public_showcase_opt_in_and_sanitised(client, make_user):
    h = auth(make_user(role='manager')['token'])
    cust = client.post('/api/customers', headers=h, json={'company_name': 'Acme'}).get_json()
    client.post('/api/projects', headers=h, json={
        'name': 'Public One', 'customer_id': cust['id'], 'showcase': True,
        'project_type': 'Web Application', 'tech_stack': ['React', 'Flask'],
        'live_url': 'https://x.co', 'budget': 99999})
    client.post('/api/projects', headers=h, json={'name': 'Private One', 'customer_id': cust['id']})

    # public, no auth header
    data = client.get('/api/public/showcase').get_json()
    titles = [p['title'] for p in data['projects']]
    assert 'Public One' in titles
    assert 'Private One' not in titles            # only showcase=True projects

    pub = next(p for p in data['projects'] if p['title'] == 'Public One')
    assert pub['tech_stack'] == ['React', 'Flask']
    assert pub['live_url'] == 'https://x.co'
    # sanitised — no client or financial data leaks
    assert 'customer_id' not in pub and 'budget' not in pub and 'contract_value' not in pub

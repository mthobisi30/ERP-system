"""Task filtering used by the project workspace."""
from tests.conftest import auth


def test_tasks_filter_by_project(client, make_user):
    h = auth(make_user(role='manager')['token'])
    p1 = client.post('/api/projects', headers=h, json={'name': 'P1'}).get_json()
    p2 = client.post('/api/projects', headers=h, json={'name': 'P2'}).get_json()

    client.post('/api/tasks', headers=h, json={'title': 'A', 'project_id': p1['id'], 'status': 'todo'})
    client.post('/api/tasks', headers=h, json={'title': 'B', 'project_id': p1['id'], 'status': 'todo'})
    client.post('/api/tasks', headers=h, json={'title': 'C', 'project_id': p2['id'], 'status': 'todo'})

    r = client.get(f'/api/tasks?project_id={p1["id"]}', headers=h).get_json()
    assert r['total'] == 2
    titles = {t['title'] for t in r['tasks']}
    assert titles == {'A', 'B'}
    # to_dict now exposes project_id
    assert all(t['project_id'] == p1['id'] for t in r['tasks'])

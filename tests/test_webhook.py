from conduit.extensions import mongo

def test_unauthorized_header(client):
    """Rejects requests missing the X-Github-Event header"""
    response = client.post('/webhook/receiver', json={})
    assert response.status_code == 401

def test_invalid_payload(client):
    """Rejects malformed JSON body"""
    headers = {'X-Github-Event': 'push'}
    response = client.post('/webhook/receiver', data="not-json", headers=headers)
    assert response.status_code == 400

def test_identify_merge_vs_pr(client):
    """Test whether a pull request is correctly parsed as a pull or merge"""
    headers = {'X-Github-Event': 'pull_request'}
    
    pr_payload = {
        'action': 'opened',
        'pull_request': {
            'id': 12345,
            'user': {'login': 'Travis'},
            'merged': False,
            'head': {'ref': 'staging'},
            'base': {'ref': 'master'},
            'updated_at': '2026-03-01T10:00:00Z'
        }
    }
    client.post('/webhook/receiver', json=pr_payload, headers=headers)
    
    merge_payload = pr_payload.copy()
    merge_payload['action'] = 'closed'
    merge_payload['pull_request']['updated_at'] = '2026-04-07T10:00:00Z'
    merge_payload['pull_request']['merged'] = True
    client.post('/webhook/receiver', json=merge_payload, headers=headers)

    events = client.get('/events').get_json()['events']
    assert events[0]['action'] == 'MERGE'
    assert events[1]['action'] == 'PULL_REQUEST'

def test_push_event_parsing(client):
    """Tests whether a push event is identified"""
    headers = {'X-Github-Event': 'push'}
    payload = {
        'after': 'sha123abc',
        'pusher': {'name': 'Travis'},
        'ref': 'refs/heads/production',
        'head_commit': {'timestamp': '2026-03-01T09:30:00Z'}
    }
    response = client.post('/webhook/receiver', json=payload, headers=headers)
    assert response.status_code == 200

    event = client.get('/events').get_json()['events'][0]
    assert event['author'] == 'Travis'
    assert event['to_branch'] == 'production'
    assert event['request_id'] == 'sha123abc'

import time

def test_polling_with_timestamp_filter(client):
    """Tests if latest updated reflect on the DB for polling by UI"""
    mongo.db.events.insert_one({
        'author': 'OldUser', 'timestamp': '2026-03-01T12:00:00Z', 'action': 'PUSH'
    })
    
    last_poll_time = '2026-03-01T12:00:01Z'
    
    mongo.db.events.insert_one({
        'author': 'NewUser', 'timestamp': '2026-03-01T12:00:15Z', 'action': 'PUSH'
    })

    response = client.get(f'/events?after={last_poll_time}')
    data = response.get_json()
    
    assert len(data['events']) == 1
    assert data['events'][0]['author'] == 'NewUser'
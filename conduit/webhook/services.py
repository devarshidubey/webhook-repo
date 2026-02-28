from conduit.extensions import mongo

def parse_event(payload, event_type):
    if event_type == 'push':
        return {
            'request_id': payload['after'],
            'author': payload['pusher']['name'],
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': payload['ref'].replace('refs/heads/', ''),
            'timestamp': payload['head_commit']['timestamp'],
        }

    elif event_type == 'pull_request':
        pr = payload['pull_request']
        merged = payload.get('action') == 'closed' and pr.get('merged')

        return {
            'request_id': str(pr['id']),
            'author': pr['user']['login'],
            'action': 'MERGE' if merged else 'PULL_REQUEST',
            'from_branch': pr['head']['ref'],
            'to_branch': pr['base']['ref'],
            'timestamp': pr['updated_at'],
        }

def save_event(data):
    mongo.db.events.insert_one(data)

def get_latest_events(after_timestamp = None):
    query = {}
    if after_timestamp:
        query = { 'timestamp': { '$gte': after_timestamp } }
    
    return list(
        mongo.db.events
        .find(query, { '_id': 0 })
        .sort('timestamp', -1)
    )
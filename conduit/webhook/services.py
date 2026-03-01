from conduit.extensions import mongo
from conduit.utils import normalize_timestamp

def parse_event(payload, event_type):
    #the payload format referred from https://docs.github.com/en/webhooks/webhook-events-and-payloads
    if event_type == 'push':
        return {
            'request_id': payload['after'],
            'author': payload['pusher']['name'],
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': payload['ref'].replace('refs/heads/', ''),
            'timestamp': normalize_timestamp(payload['head_commit']['timestamp']), #Github sends the IST ISO string, needs normalizaton
        }https://docs.github.com/en/webhooks/webhook-events-and-payloads

    elif event_type == 'pull_request':
        pr = payload['pull_request']
        merged = payload.get('action') == 'closed' and pr.get('merged')

        return {
            'request_id': str(pr['id']),
            'author': pr['user']['login'],
            'action': 'MERGE' if merged else 'PULL_REQUEST',
            'from_branch': pr['head']['ref'],
            'to_branch': pr['base']['ref'],
            'timestamp': normalize_timestamp(pr['updated_at']),
        }

def save_event(data):
    mongo.db.events.insert_one(data)

#pagination based on timestamp: faster than offset cursor
#fits well with the 15 sec polling window
def get_latest_events(after_timestamp = None): 
    query = {}
    if after_timestamp:
        query = { 'timestamp': { '$gt': after_timestamp } }
    
    return list(
        mongo.db.events
        .find(query, { '_id': 0 })
        .sort('timestamp', -1)
    )
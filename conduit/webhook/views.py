from flask import Blueprint, request, jsonify
from conduit.exceptions import InvalidUsage
from .serializers import event_schema, events_schema
from .services import parse_event, save_event, get_latest_events

blueprint = Blueprint('webhooks', __name__)

@blueprint.route('/webhook/receiver', methods=['POST'])
def webhook():
    #The github headers need to be verified before processing the request
    event_type = request.headers.get('X-Github-Event')
    if not event_type:
        raise InvalidUsage.unauthorized()

    payload = request.get_json(silent=True)
    if payload is None:
        raise InvalidUsage.invalid_payload()
    
    if event_type == 'ping': #This was added to allow the webhook integration with github: sends a ping as the first event
        return jsonify({'message': 'pong'}), 200
    
    try:
        data = parse_event(payload, event_type)
    except (KeyError, ValueError):
        raise InvalidUsage.invalid_payload()
    
    errors = event_schema.validate(data)
    if errors:
        raise InvalidUsage.invalid_payload()
    
    save_event(data)
    return jsonify(({ 'message': 'success' })), 200

@blueprint.route('/events', methods=['GET'])
def events():
    after_timestamp = request.args.get('after', None)
    data = get_latest_events(after_timestamp)
    return jsonify({'events': events_schema.dump(data)}), 200
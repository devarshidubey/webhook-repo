from marshmallow import Schema, fields, validate, ValidationError

class EventSchema(Schema):
    request_id = fields.Str(required=True)
    author = fields.Str(required=True)
    action = fields.Str(required=True, validate=validate.OneOf(['PUSH', 'PULL_REQUEST', 'MERGE']))
    from_branch = fields.Str(load_default=None)
    to_branch = fields.Str(required=True)
    timestamp = fields.Str(required=True)

event_schema = EventSchema()
events_schema = EventSchema(many=True)

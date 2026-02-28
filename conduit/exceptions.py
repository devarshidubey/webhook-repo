from flask import jsonify


def template(data, code=500):
    return {'message': {'errors': {'body': data}}, 'status_code': code}


INVALID_PAYLOAD = template(['Invalid JSON payload'], code=400)
UNAUTHORIZED = template(['Unauthorized'], code=401)
UNKNOWN_ERROR = template([], code=500)


class InvalidUsage(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = self.message
        return jsonify(rv)

    @classmethod
    def invalid_payload(cls):
        return cls(**INVALID_PAYLOAD)

    @classmethod
    def unauthorized(cls):
        return cls(**UNAUTHORIZED)

    @classmethod
    def unknown_error(cls):
        return cls(**UNKNOWN_ERROR)
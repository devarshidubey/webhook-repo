import pytest
from conduit.app import create_app
from conduit.settings import TestConfig
from conduit.extensions import mongo

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        mongo.db.events.delete_many({})

@pytest.fixture
def client(app):
    return app.test_client()
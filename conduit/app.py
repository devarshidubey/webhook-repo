from flask import Flask
from conduit import commands, webhook
from conduit.extensions import cors, mongo
from conduit.exceptions import InvalidUsage

def create_app(config_object):
    #application factory

    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    
    register_blueprints(app)
    register_extensions(app)
    register_errorhandlers(app)
    register_commands(app)

    return app

def register_extensions(app):
    mongo.init_app(app)

def register_blueprints(app):
    origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    cors.init_app(app, origins=origins) #to protect the Web API: GET /events

    app.register_blueprint(webhook.views.blueprint)

def register_commands(app):
    #Commands to oraganize and test durign dev
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)

def register_errorhandlers(app):
    
    def errorhandler(error):
        response = error.to_json()
        response.status_code = error.status_code
        return response
    
    app.errorhandler(InvalidUsage)(errorhandler)
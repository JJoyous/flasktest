from flask import Flask, Blueprint
# from flask_session import Session
import API


def add_routes(flask):
    for attr in dir(API):
        if attr.startswith('_'):
            continue
        val = getattr(API, attr)
        if isinstance(val, Blueprint):
            flask.register_blueprint(val)
    return flask


def create_app():
    flask = Flask(__name__)
    # flask.config.from_object(config)
    flask = add_routes(flask)
    # Session(flask)
    return flask


app = create_app()

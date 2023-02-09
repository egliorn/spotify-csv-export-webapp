from flask import Flask, session
from .spotify_handler import SpotifyHandler


spotify = SpotifyHandler()


def init_app():
    """Initialize core app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Development')

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    with app.app_context():
        # blueprints
        from . import main, auth, error_handler
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(error_handler.bp)

        return app

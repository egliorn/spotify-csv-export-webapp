from flask import Flask, session, request
from flask_babel import Babel
from .spotify_handler import SpotifyHandler


spotify = SpotifyHandler()
babel = Babel()


def init_app():
    """Initialize core app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Development')

    # babel
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])  # best lang match
    babel.init_app(app, locale_selector=get_locale)

    # permanent session
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

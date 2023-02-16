from flask import Flask, session, request
from flask_babel import Babel
from .spotify_handler import SpotifyHandler
from flask_caching import Cache


spotify = SpotifyHandler()
babel = Babel()
cache = Cache()


def init_app():
    """Initialize core app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Deployment')

    # permanent session
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # babel
    def get_locale():
        lang = session.get('lang', None)
        if lang is not None:  # if lang already in session
            return session.get('lang')
        lang = request.accept_languages.best_match(app.config['LANGUAGES'])  # best lang match
        session['lang'] = lang
        return lang

    # init plugins
    babel.init_app(app, locale_selector=get_locale)
    cache.init_app(app)

    with app.app_context():
        # blueprints
        from . import main, auth, error_handler
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(error_handler.bp)

        return app

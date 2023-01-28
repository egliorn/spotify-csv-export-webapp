from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .spotify_handler import SpotifyHandler


db = SQLAlchemy()
login_manager = LoginManager()
spotify = SpotifyHandler()


def init_app():
    """Initialize core app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Development')

    # init plugins
    db.init_app(app)
    login_manager.init_app(app)

    from .models import User  # import User model from here to avoid circular import

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    with app.app_context():
        # blueprints
        from . import main, auth
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)

        return app

from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
import tekore as tk
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User


bp = Blueprint('auth', __name__)

CONF = tk.config_from_environment()
CRED = tk.Credentials(*CONF)
SCOPES = [
    'user-library-read',
    'playlist-read-collaborative',
    'playlist-read-private',
]
auths = {}  # Ongoing authorisations: state -> UserAuth
spotify = tk.Spotify()


def refresh_token(token):
    """Refresh an access token and update in db."""
    user = User.session.filter_by(spotify_id=current_user.spotify_id)
    user.spotify_token = CRED.refresh(token)


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.results'))

    auth = tk.UserAuth(cred=CRED, scope=SCOPES)
    auths[auth.state] = auth

    return redirect(auth.url)


@bp.route('/callback')
def login_callback():
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    auth = auths.pop(state, None)

    if auth is None:
        return 'Invalid state', 400

    token = auth.request_token(code, state)

    with spotify.token_as(token):
        spotify_id = spotify.current_user().id

    try:
        user = User(
            spotify_id=spotify_id,
            token_object=token
        )
        db.session.add(user)
        db.session.commit()

    except IntegrityError:  # if user with spotify_id already exists in db
        db.session.rollback()

        user = User.query.filter_by(spotify_id=spotify_id).first()
        user.token_object = token
        db.session.commit()

    login_user(user, remember=True)

    return redirect(url_for('main.results'))


@bp.route('/logout')
@login_required
def logout():
    user = User.query.filter_by(spotify_id=current_user.spotify_id).first()
    db.session.delete(user)
    db.session.commit()

    logout_user()

    return redirect(url_for('main.index'))

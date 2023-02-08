from flask import Blueprint, redirect, request, url_for, abort, session
import tekore as tk
from . import spotify
import jsonpickle
from functools import wraps


bp = Blueprint('auth', __name__)

CONF = tk.config_from_environment()
CRED = tk.Credentials(*CONF)
SCOPES = [
    'user-library-read',
    'playlist-read-collaborative',
    'playlist-read-private',
]
auths = {}  # Ongoing authorisations: state -> UserAuth


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username', None) is None:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def refresh_token(token):
    """Refreshes the Spotify access token in db and current_user."""
    if token.is_expiring:
        refreshed_token = CRED.refresh(token)
        session['token'] = jsonpickle.encode(refreshed_token)


@bp.route('/login')
def login():
    user = session.get('username', None)
    token = session.get('token', None)

    if user is not None and token is not None:
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
        abort(400)

    token = auth.request_token(code, state)

    with spotify.token_as(token):
        spotify_id = spotify.current_user().id

    session['username'] = spotify_id
    session['token'] = jsonpickle.encode(token)

    return redirect(url_for('main.results'))


@bp.route('/logout')
@login_required
def logout():
    session.pop('username')
    session.pop('token')
    return redirect(url_for('main.index'))

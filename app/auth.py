from flask import Blueprint, redirect, request, url_for, abort, session, flash
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
    """Redirect to /index, if userid and token not in session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('userid') and session.get('token'):
            flash("You need to be signed in to access this page.")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def refresh_token(token):
    """:returns refreshed Spotify token."""
    return CRED.refresh(token)


@bp.route('/login')
def login():
    if session.get('userid') and session.get('token'):  # redirect to /results if userid and token in session
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

    session['userid'] = spotify_id
    session['token'] = jsonpickle.encode(token)

    return redirect(url_for('main.results'))


@bp.route('/logout')
@login_required
def logout():
    session.pop('userid')
    session.pop('token')
    return redirect(url_for('main.index'))

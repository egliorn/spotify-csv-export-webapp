from flask import Blueprint, render_template
from flask_login import current_user, login_required
import tekore as tk
from .auth import refresh_token


bp = Blueprint('main', __name__)

spotify = tk.Spotify()


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/results')
@login_required
def results():
    token = current_user.token_object

    if token.is_expiring:
        refresh_token(token)

    with spotify.token_as(token):
        username = spotify.current_user().display_name
        return f'{username}'

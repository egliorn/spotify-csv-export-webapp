from flask import Blueprint, render_template, request, send_file, session, g, redirect, url_for
from .auth import refresh_token, login_required
from .file_handler import generate_csv, generate_zip
from . import spotify, babel
import jsonpickle


bp = Blueprint('main', __name__)


def get_token():
    """:returns Spotify token from the session."""
    if 'token' not in g:
        g.token = jsonpickle.decode(session['token'])
    return g.token


@bp.before_request
def update_token():
    """Refresh and put token to session if token expiring."""
    if session.get('userid') and session.get('token'):  # check if userid and token in session
        token = get_token()
        if token.is_expiring:
            session['token'] = jsonpickle.encode(refresh_token(token))  # put refreshed token to session


@bp.app_template_filter()
def playlist_image_filter(images):
    """:returns 'medium', 'large' or placeholder photo image of playlist."""
    if images:
        try:
            return images[-2].url  # try to pick “medium” image
        except IndexError:
            return images[-1].url  # pick “large”, if no other images

    return "static/img/spotify_playlist_ph.png"  # if playlist doesn't have images


@bp.route('/lang_pick')
def lang_picker():
    prev_page = request.referrer  # link to previous page
    session['lang'] = request.args.get('lang')
    return redirect(prev_page)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/results')
@login_required
def results():
    token = get_token()

    with spotify.token_as(token):
        saved_tracks = spotify.saved_tracks()
        saved_playlists = spotify.saved_playlists_simple()

    return render_template('results.html', saved_tracks=saved_tracks, saved_playlists=saved_playlists)


@bp.route('/download/csv')
@login_required
def send_csv():
    token = get_token()

    playlist_id = request.args.get('id')
    playlist_name = request.args.get('name')

    with spotify.token_as(token):
        if playlist_id:
            track_paging = spotify.playlist_tracks(playlist_id)
        else:
            track_paging = spotify.saved_tracks()

        playlist_contents = spotify.playlist_unpack(track_paging)

    csv_file = generate_csv(playlist_contents)

    return send_file(csv_file, download_name=f"{playlist_name}.csv", mimetype='text/csv')


@bp.route('/download/zip')
@login_required
def send_zip():
    token = get_token()

    with spotify.token_as(token):
        saved_tracks = spotify.saved_tracks()  # SavedTrackPaging
        saved_playlists = spotify.saved_playlists_full()  # PlaylistTrackPaging

        # csv_files dict: playlist name -> BytesIO csv file
        csv_files = {"Liked Songs": generate_csv(spotify.playlist_unpack(saved_tracks))}  # add 'liked songs'

        for playlist in saved_playlists:  # add all saved playlists
            playlist_contents = spotify.playlist_unpack(playlist.tracks)
            csv_files[playlist.name] = generate_csv(playlist_contents)

    zip_file = generate_zip(csv_files)

    return send_file(
        zip_file,
        download_name='spotify library.zip'
    )

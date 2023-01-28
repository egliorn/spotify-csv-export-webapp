from flask import Blueprint, render_template, request, send_file
from flask_login import current_user, login_required
from .auth import refresh_token
from . import spotify
from .file_handler import generate_csv, generate_zip


bp = Blueprint('main', __name__)


@bp.before_request
def refresh_token_wrap():
    if current_user.is_authenticated:
        refresh_token(current_user.token_object)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/results')
@login_required
def results():
    token = current_user.token_object

    with spotify.token_as(token):
        saved_tracks = spotify.saved_tracks()
        saved_playlists = spotify.saved_playlists_simple()

    return render_template('results.html', saved_tracks=saved_tracks, saved_playlists=saved_playlists)


@bp.route('/download/csv')
@login_required
def send_csv():
    token = current_user.token_object

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
    token = current_user.token_object

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
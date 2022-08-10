from flask import Flask, abort, url_for, request, redirect, render_template, session, send_file
from application.user_auth import UserAuth, auths
from application.spotify_handler import SpotifyHandler
from application.file_handler import generate_csv, generate_zip


users = {}  # Spotify user ID -> SpotifyHandler


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if 'user' in session:
            return redirect(url_for('results'))

        if request.method == 'POST':
            auth = UserAuth()
            auths[auth.state] = auth

            return redirect(auth.url)
        return render_template('index.html')

    @app.route('/callback', methods=['GET'])
    def login_callback():
        if request.args.get('error') == 'access_denied':
            abort(401)

        code = request.args.get('code')
        state = request.args.get('state')
        auth = auths.pop(state)

        if auth is None:
            abort(400)

        token = auth.get_token(code, state)

        spotify = SpotifyHandler(token)
        spotify_user_id = spotify.current_user().id
        users[spotify_user_id] = spotify
        session['user'] = spotify_user_id

        return redirect(url_for('results'))

    @app.route('/results', methods=['GET'])
    def results():
        user = session.get('user')
        spotify = users.get(user)

        if spotify.token.is_expiring:
            spotify.refresh_token()

        username = spotify.get_username()
        saved_tracks = spotify.get_saved_tracks()
        saved_playlists = spotify.get_saved_playlists()

        return render_template(
            'results.html',
            username=username,
            saved_tracks=saved_tracks,
            saved_playlists=saved_playlists
        )

    @app.route('/download/csv')
    def send_csv():
        user = session.get('user')
        spotify = users.get(user)

        playlist_id = request.args.get('playlist_id')
        playlist_name = request.args.get('playlist_name')

        if playlist_id == "0":
            playlist_contents = spotify.playlist_unpack(spotify.get_saved_tracks())
        else:
            playlist_contents = spotify.playlist_unpack(spotify.get_playlist_tracks(playlist_id))

        csv_file = generate_csv(playlist_contents)
        return send_file(
            csv_file,
            download_name=f"{playlist_name}.csv",
            mimetype='text/csv'
        )

    @app.route('/download/zip')
    def send_zip():
        user = session.get('user')
        spotify = users.get(user)

        saved_tracks = spotify.get_saved_tracks()  # SavedTrackPaging
        saved_playlists = spotify.get_saved_playlists()  # PlaylistTrackPaging

        # playlist name -> BytesIO csv file
        csv_files = {"Liked tracks": generate_csv(spotify.playlist_unpack(saved_tracks))}
        for playlist in saved_playlists:
            playlist_contents = spotify.playlist_unpack(playlist.tracks)
            csv_files[playlist.name] = generate_csv(playlist_contents)

        zip_file = generate_zip(csv_files)

        return send_file(
            zip_file,
            download_name='spotify library.zip'
        )

    @app.route('/logout', methods=['GET'])
    def logout():
        uid = session.pop('user', None)
        if uid is not None:
            users.pop(uid, None)

        return redirect(url_for('home'))

    @app.route('/info', methods=['GET'])
    def info():
        return render_template('info.html')

    return app

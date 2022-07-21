from flask import Flask, request, redirect, render_template, session, url_for
from application.user_auth import UserAuth, auths
from application.spotify_handler import SpotifyHandler

users = {}  # UserAuth.state(user ID) -> SpotifyHandler


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    @app.route('/', methods=['GET'])
    def home():
        if 'user' in session:
            return redirect(url_for('results'))
        return render_template('index.html')

    @app.route('/info', methods=['GET'])
    def info():
        return render_template('info.html')

    @app.route('/login', methods=['GET'])
    def login():
        if 'user' in session:
            return redirect(url_for('results'))

        auth = UserAuth()
        auths[auth.state] = auth

        return redirect(auth.url)

    @app.route('/callback', methods=['GET'])
    def login_callback():
        code = request.args.get('code')
        state = request.args.get('state')
        auth = auths.pop(state)

        if auth is None:
            return 'Invalid state!', 400

        token = auth.get_token(code, state)
        session['user'] = state  # adds user to flask-session
        users[state] = SpotifyHandler(token)

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

        return render_template('results.html', username=username, saved_tracks=saved_tracks,
                               saved_playlists=saved_playlists)

    @app.route('/download/<playlist_id>.csv')
    def generate_csv(playlist_id):
        user = session.get('user')
        spotify = users.get(user)

        if playlist_id == "liked_tracks":
            playlist = spotify.get_saved_tracks()
        else:
            playlist = spotify.get_playlist_tracks(playlist_id)

        playlist_contents = spotify.playlist_unpack(playlist)

        def generate():
            for row in playlist_contents:
                yield f"{','.join(row)}\n"

        return app.response_class(generate(), mimetype='text/csv')

    @app.route('/logout', methods=['GET'])
    def logout():
        uid = session.pop('user', None)
        if uid is not None:
            users.pop(uid, None)

        return redirect(url_for('home'))

    return app

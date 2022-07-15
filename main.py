from flask import Flask, request, redirect, render_template, session, url_for
from user_auth import UserAuth, auths, refresh_token
from spotify_handler import SpotifyHandler

users = {}  # User tokens: UserAuth.state(user ID) -> token

app = Flask(__name__)
app.config['SECRET_KEY'] = '_'


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
    users[state] = token

    return redirect(url_for('results'))


@app.route('/results', methods=['GET'])
def results():
    user = session.get('user')
    token = users.get(user)

    if token.is_expiring:
        token = refresh_token(token)
        users[user] = token

    spotify = SpotifyHandler(token)
    username = spotify.get_username()
    saved_tracks = spotify.get_saved_tracks()
    saved_playlists = spotify.get_saved_playlists()

    return render_template('results.html', username=username, saved_tracks=saved_tracks, saved_playlists=saved_playlists)


@app.route('/logout', methods=['GET'])
def logout():
    uid = session.pop('user', None)
    if uid is not None:
        users.pop(uid, None)

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

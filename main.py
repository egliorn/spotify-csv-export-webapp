import tekore as tk
from flask import Flask, request, redirect, render_template, session, url_for

conf = tk.config_from_environment()
cred = tk.Credentials(*conf)
spotify = tk.Spotify()

auths = {}  # Ongoing authorisations: state -> UserAuth
users = {}  # User tokens: state -> token (use state as a user ID)

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

    scopes = tk.scope.every
    auth = tk.UserAuth(cred, scope=scopes)
    auths[auth.state] = auth

    return redirect(auth.url)


@app.route('/callback', methods=['GET'])
def login_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    auth = auths.pop(state)

    if auth is None:
        return 'Invalid state!', 400

    token = auth.request_token(code, state)
    session['user'] = state
    users[state] = token

    return redirect(url_for('results'))


@app.route('/results', methods=['GET'])
def results():
    user = session.get('user')
    token = users.get(user)

    if token.is_expiring:
        token = cred.refresh(token)
        users[user] = token

    with spotify.token_as(token):
        spotify_user = spotify.current_user()
        username = spotify_user.display_name
        userid = spotify_user.id

        # users saved tracks, SavedTrackPaging
        saved_tracks = spotify.saved_tracks()

        # users saved playlists, PlaylistTrackPaging
        user_playlists = spotify.playlists(user_id=userid)
        playlists_ids = [pl.id for pl in user_playlists.items]
        saved_playlists = [spotify.playlist(playlist_id) for playlist_id in playlists_ids]

    return render_template('results.html', username=username, saved_tracks=saved_tracks, saved_playlists=saved_playlists)


@app.route('/logout', methods=['GET'])
def logout():
    uid = session.pop('user', None)
    if uid is not None:
        users.pop(uid, None)

    return redirect(url_for('home'))


@app.route('/test')
def test():
    uses = [f'{user}<br>' for user in users]
    return f"{uses}"


if __name__ == '__main__':
    app.run(debug=True)

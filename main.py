import tekore as tk
from flask import Flask, request, redirect, render_template, session, url_for, send_file
import csv

conf = tk.config_from_environment()
cred = tk.Credentials(*conf)
spotify = tk.Spotify()

auths = {}
users = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = '_'


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    scopes = [
        tk.scope.every
    ]
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


@app.route('/results')
def results():
    user = session.get('user')
    token = users.get(user)

    with spotify.token_as(token):
        first_items = spotify.saved_tracks()

        saved_tracks = []
        for item in spotify.all_items(first_items):
            saved_tracks.append(
                {
                    'track_name': item.track.name,
                    'artists': ",".join([artist.name for artist in item.track.artists]),
                    'album': item.track.album.name
                }
            )

    return render_template('results.html', saved_tracks=saved_tracks)


if __name__ == '__main__':
    app.run(debug=True)

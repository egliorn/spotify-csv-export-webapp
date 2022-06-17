from api_caller import ApiCaller, auths, users
from flask import Flask, request, redirect, render_template, session, url_for


app = Flask(__name__)
app.config['SECRET_KEY'] = '_'

api_caller = ApiCaller()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    auth_url = api_caller.get_auth_url()
    return redirect(auth_url)


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

    saved_tracks = api_caller.get_results(token)

    return render_template('results.html', saved_tracks=saved_tracks)


if __name__ == '__main__':
    app.run(debug=True)

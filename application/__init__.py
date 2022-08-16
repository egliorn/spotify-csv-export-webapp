from flask import Flask, abort, url_for, request, redirect, render_template, session, send_file
from flask_sqlalchemy import SQLAlchemy
from application.user_auth import UserAuth, auths, refresh_token
from application.spotify_handler import SpotifyHandler
from application.file_handler import generate_csv, generate_zip
from datetime import timedelta, datetime
from functools import wraps


def login_required(f):
    """Redirect to '401' if user not in flask.session"""
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'user' not in session:
            return abort(401)
        return f(*args, **kwargs)
    return decorated_func


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db = SQLAlchemy(app)
    spotify = SpotifyHandler()

    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.String, primary_key=True)
        created = db.Column(db.DateTime, default=datetime.utcnow)
        token_object = db.Column(db.PickleType())
    db.create_all()

    @app.before_request
    def make_session_permanent():  # "remember me" functionality
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)

    @app.route('/', methods=['GET', 'POST'])
    def home():
        if 'user' in session:
            return redirect(url_for('results'))

        if request.method == 'POST':
            auth = UserAuth()  # user authorisation flow
            auths[auth.state] = auth

            return redirect(auth.url)  # redirect for authorisation via spotify account service
        return render_template('index.html')

    @app.route('/callback', methods=['GET'])
    def login_callback():
        if request.args.get('error') == 'access_denied':  # 401 if access denied
            abort(401)

        code = request.args.get('code')
        state = request.args.get('state')
        auth = auths.pop(state)

        if auth is None:  # additional state for protection
            abort(400)

        token = auth.get_token(code, state)

        with spotify.token_as(token):  # get spotify user id
            user_id = spotify.current_user().id

        user = User.query.filter_by(id=user_id).first()
        if user is None:  # create entry if user not in db
            user = User(id=user_id, token_object=token)
            db.session.add(user)
            db.session.commit()
        else:  # update entry if user in db
            user.token_object = token
            db.session.commit()

        session['user'] = user_id

        return redirect(url_for('results'))

    @app.route('/results', methods=['GET'])
    @login_required
    def results():
        user_id = session.get('user')
        token = User.query.filter_by(id=user_id).first().token_object

        with spotify.token_as(token):
            if spotify.token.is_expiring:
                token = refresh_token(token)

                user = User.query.get(user_id)
                user.token_object = token
                db.session.commit()

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
    @login_required
    def send_csv():
        user_id = session.get('user')
        token = User.query.filter_by(id=user_id).first().token_object

        playlist_id = request.args.get('playlist_id')
        playlist_name = request.args.get('playlist_name')

        with spotify.token_as(token):
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
    @login_required
    def send_zip():
        user_id = session.get('user')
        token = User.query.filter_by(id=user_id).first().token_object

        with spotify.token_as(token):
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
    @login_required
    def logout():
        user_id = session.pop('user', None)
        if user_id is not None:
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()

        return redirect(url_for('home'))

    @app.route('/info', methods=['GET'])
    def info():
        return render_template('info.html')

    return app

import tekore as tk

auths = {}
users = {}


class ApiCaller:
    conf = tk.config_from_environment()
    cred = tk.Credentials(*conf)
    spotify = tk.Spotify()

    @staticmethod
    def get_auth_url():
        scopes = [
            tk.scope.every
        ]
        auth = tk.UserAuth(ApiCaller.cred, scope=scopes)
        auths[auth.state] = auth
        return auth.url

    @staticmethod
    def get_results(token):
        with ApiCaller.spotify.token_as(token):
            first_items = ApiCaller.spotify.saved_tracks()

            saved_tracks = []
            for item in ApiCaller.spotify.all_items(first_items):
                saved_tracks.append(
                    {
                        'track_name': item.track.name,
                        'artists': ",".join([artist.name for artist in item.track.artists]),
                        'album': item.track.album.name
                    }
                )
            return saved_tracks

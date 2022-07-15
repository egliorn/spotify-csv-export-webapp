import tekore as tk


class SpotifyHandler(tk.Spotify):
    """tekore.Spotify, client to WEB API endpoints"""

    def __init__(self, token):
        super().__init__()
        self.token = token

    def get_username(self):
        """:returns spotify username of current user"""
        return self.current_user().display_name

    def get_saved_tracks(self):
        """:returns user's saved tracks, 'SavedTrackPaging'"""
        return self.saved_tracks()

    def get_saved_playlists(self):
        """:returns a list of all user's playlists, 'PlaylistTrackPaging'"""
        user_id = self.current_user().id
        user_playlists = self.playlists(user_id=user_id)
        playlists_ids = [pl.id for pl in user_playlists.items]

        return [self.playlist(playlist_id) for playlist_id in playlists_ids]

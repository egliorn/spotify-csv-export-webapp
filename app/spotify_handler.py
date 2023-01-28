from flask_login import current_user
from tekore import Spotify


class SpotifyHandler(Spotify):
    """tekore.Spotify, client to WEB API endpoints. """

    def __init__(self):
        super().__init__()

    # for /results
    def saved_playlists_simple(self):
        """:returns user's saved playlists, 'SimplePlaylistPaging'. """
        return self.playlists(user_id=current_user.spotify_id)

    # for export to .csv
    def saved_playlists_full(self):
        """:returns a list of all user's playlists, 'FullPlaylist'. """
        user_playlists = self.playlists(user_id=current_user.spotify_id)
        playlists_ids = [pl.id for pl in user_playlists.items]

        return [self.playlist(playlist_id) for playlist_id in playlists_ids]

    def playlist_tracks(self, playlist_id):
        """:returns playlist's tracks, 'TrackPaging'. """
        return self.playlist(playlist_id).tracks

    def playlist_unpack(self, track_paging):
        """:returns contents of given 'SavedTrackPaging' or 'PlaylistTrackPaging'. """
        contents = [["track_uri", "track_name", "artists", "album", "duration"]]
        for item in self.all_items(track_paging):
            contents.append(
                [
                    item.track.uri,
                    item.track.name,
                    ", ".join([artist.name for artist in item.track.artists]),
                    item.track.album.name,
                    f"{round(item.track.duration_ms / 1000)}sec"
                ]
            )

        return contents

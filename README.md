# spotify-to-csv-export-webapp
A web app, for exporting saved tracks and playlists of a Spotify user in CSV format.

Based on [Flask](https://github.com/pallets/flask) framework. Uses [Tekore](https://github.com/felix-hilden/tekore) as a Spotify Web API client.

Used [scopes](https://developer.spotify.com/documentation/general/guides/authorization/scopes/):
- user-read-email, for Spotify userid and username 
- user-library-read 
- playlist-read-collaborative 
- playlist-read-private
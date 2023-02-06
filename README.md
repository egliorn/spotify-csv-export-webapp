# spotify-to-csv-export-webapp
Web app, to export saved tracks and playlists of Spotify user in CSV format.

Stack: Flask, [Tekore](https://github.com/felix-hilden/tekore) _(Spotify Web API client)_, Bootstrap 5.

Used [scopes](https://developer.spotify.com/documentation/general/guides/authorization/scopes/):
- user-library-read 
- playlist-read-collaborative 
- playlist-read-private

## How to use
1. Open website.
2. Click `Sign in with Spotify`.
3. Confirm access by clicking `I ACCEPT`.
4. All your Spotify playlists will appear. Here you can download separate playlists or just download all.

Exported `playlist_name.csv` structure:
- **track_uri**: Spotify track uri, can be used for [re-import](#re-import-to-spotify).
- **track_name**
- **artists**: comma—separated list of artists.
- **album**: album name.
- **duration**

____
### Re-import to Spotify
:exclamation: **Only works in the Spotify desktop app**.

After saving playlists:
1. Create a playlist in Spotify.
2. Copy from `playlist_name.csv` the values of the `track_uri` column
(example value: `spotify:track:2FJyRsWesaxh5nOTDQWBMw`).
3. Paste into the Spotify playlist page.

____
#### :grey_exclamation: Note if you are using MS Excel:
If you use Excel to open `playlist_name.csv` - non-english characters may be displayed in incorrect encoding.
To fix this – use different app or check this solutions:
- https://stackoverflow.com/a/6488070
- [https://answers.microsoft.com/](https://answers.microsoft.com/en-us/msoffice/forum/all/how-to-open-utf-8-csv-file-in-excel-without-mis/1eb15700-d235-441e-8b99-db10fafff3c2)
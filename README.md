# music-playlist-ingester
Import playlists exported from itunes into spotify

## Example Usage
`SPOTIPY_CLIENT_ID=$YOUR_CLIENT_ID SPOTIPY_CLIENT_SECRET=$YOUR_CLIENT_SECRET SPOTIPY_REDIRECT_URI=$YOUR_REDIRECT_URL python ingest_playlist.py /path/to/itunes_playlist.xml $SPOTIFY_USER_ID "playlist name to create in spotify"`

see Spotify API docs to create your developer tokens: https://developer.spotify.com/

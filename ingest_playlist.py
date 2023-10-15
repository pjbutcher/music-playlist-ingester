import typer
import spotipy
import xml.etree.ElementTree as ET
from more_itertools import chunked
from spotipy.oauth2 import SpotifyOAuth
from spotipy.client import Spotify
from xml.etree.ElementTree import Element

# spotifiy api limits the number of tracks you can add per api call
NUM_TRACKS_PLAYLIST_LIMIT = 100

def get_tracks(xml_root: Element) ->list[Element]:
    playlist_dict = next(iter(xml_root.findall('dict')))
    tracks_dict = next(iter(playlist_dict.findall('dict')))
    return tracks_dict.findall('dict')

def track_xml_to_dict(track_xml: Element) -> dict[str, str] | None:
    # itunes xml is in the format:
    # <key_tag1>value</key_tag1><value_tag1>value<value_tag1>
    # <key_tag2>value</key_tag2><value_tag2>value<value_tag2>
    # so chunk together tags by 2 to pair up key/value tags and unpack to dict
    chunked_track_details = chunked([child.text for child in track_xml], 2, strict=True)
    track_info = {k:v for k,v in chunked_track_details}
    if not all([key in track_info for key in ['Name', 'Artist', 'Album']]):
        print(f'Itunes xml missing required metadata: {track_info}')
        return None
    return track_info

def get_spotify_id(track_info: dict[str, str], spotify: Spotify=None) -> str | None:
    query = f"artist:{track_info['Artist']} track:{track_info['Name']} album:{track_info['Album']}"
    result = spotify.search(query, type='track')
    if not result['tracks']['items']:
         print(f"Track not found in Spotify: {query}")
         return None
    return result['tracks']['items'][0]['id']

def main(file_path: str, user: str, playlist: str) -> None:

    # TODO: add option for public playlists
    scope = "playlist-modify-private"
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    playlist = spotify.user_playlist_create(user, playlist, public=False)

    tree = ET.parse(file_path)
    root = tree.getroot()
    tracks = get_tracks(root)
    spotify_ids = []
    
    # TODO: instead of going through track by track we could get unique albums 
    # and add whole albums at a time
    for track in tracks:
        track_info = track_xml_to_dict(track)
        if not track_info:
            continue
        spotify_id = get_spotify_id(track_info, spotify=spotify)
        if not spotify_id:
            continue
        spotify_ids.append(spotify_id)

    for spotify_ids_chunk in chunked(spotify_ids, NUM_TRACKS_PLAYLIST_LIMIT):
        spotify.user_playlist_add_tracks(user, playlist['id'], spotify_ids_chunk)


if __name__ == '__main__':
    typer.run(main)

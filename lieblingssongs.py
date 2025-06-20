import os
import json
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API-Zugangsdaten
CLIENT_ID = "2a584a617b164b14b79c8cb195691744"
CLIENT_SECRET = "1359a02875eb40b6a5b39a863e0e6f28"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Ziel-Playlist-ID (muss dir gehören)
TARGET_PLAYLIST_ID = "08TqgXsXb6l0rgxwYatZTm"

# Dateien für gespeicherte IDs und Log
SYNCED_FILE = "synced_tracks.json"
LOG_FILE = "spotify_sync.log"

# Authentifizierung
scope = "playlist-modify-public playlist-modify-private user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))


def write_log(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"{timestamp} {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def load_synced_ids():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_synced_ids(ids):
    with open(SYNCED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f)


def get_liked_track_ids():
    track_ids = []
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = results.get('items', [])
        if not items:
            break
        track_ids.extend([
            item['track']['id']
            for item in items
            if item['track']
        ])
        offset += 50
        print(f"Likes geladen: {offset}")
    return track_ids


def add_new_liked_songs_to_playlist():
    liked = get_liked_track_ids()
    already_synced = load_synced_ids()
    new_songs = [
        track_id for track_id in liked
        if track_id not in already_synced
    ]

    if new_songs:
        for i in range(0, len(new_songs), 100):
            sp.playlist_add_items(TARGET_PLAYLIST_ID, new_songs[i:i+100])
        write_log(f"{len(new_songs)} neue Songs hinzugefügt.")
        already_synced.update(new_songs)
        save_synced_ids(already_synced)
    else:
        write_log("Keine neuen Lieblingssongs gefunden.")


if __name__ == "__main__":
    add_new_liked_songs_to_playlist()

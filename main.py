import re
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://example.com/"
SPOTIFY_USER_ID = os.getenv("SPOTIFY_USER_ID")

# Authenticate the Spotify via Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope="playlist-modify-public"))


def get_date():
    """Get the date for which you want to check the top 100 songs"""
    while True:
        date = input("Enter the date in format YYYY-MM-DD: \n")
        # Regex for checking if passed date matches a YYYY-MM-DD format
        pattern = re.compile('^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$')
        if pattern.match(date):
            print(f'Searching for top100 Billboard songs from {date} in Spotify')
            break
        else:
            print('Incorrect date format.')
    return date


def create_new_playlist(date):
    """Create a new playlist in Spotify"""
    results = sp.user_playlist_create(user=SPOTIFY_USER_ID, 
                                    name=f"{date} python_test_playlist", 
                                    public=True,
                                    collaborative=False, 
                                    description="Python script testing playlist")
    print(f"Creating a playlist")
    playlist_id = results["uri"]
    return playlist_id

  
def get_tracks_data(date):
    """Webscrap the Billboard website with BeautifulSoup"""
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    response = requests.get(url)
    database = response.text

    soup = BeautifulSoup(database, "html.parser")

    songs = soup.select("li ul li h3")
    authors = soup.select("div ul li ul li span")

    songs_list = [song.getText().strip() for song in songs]
    authors_list_all = [author.getText().strip() for author in authors]
    authors_list = create_valid_authors_list(authors_list_all)
    return songs_list, authors_list


def is_valid(author):
    """Check if the authors name is valid"""
    if author == "-":
        return False
    else:
        try:
            int(author)
            return False
        except:
            return True


def create_valid_authors_list(authors_list_all):
    """Create the valid authors list"""
    list = []
    for author in authors_list_all:
        if is_valid(author):
            list.append(author)
    return list


def search_tracks(songs_list, authors_list):
    """Find each track in Spotify and add it to a list in form of dictionary"""
    tracks = []
    for n in range(len(songs_list)):
        print(f"Song #{n+1} added.")
        try:
            track = sp.search(q="artist:" + authors_list[n] + " track:" + songs_list[n], type="track")
            track_id = track['tracks']['items'][0]['id']
            tracks.append({'title':f'{songs_list[n]}',
                           'id':f'{track_id}',
                           'author':f'{authors_list[n]}'})
        except IndexError:
            print(f'"{songs_list[n]}" is not available in Spotify')
            continue
    return tracks


def add_tracks_to_playlist(playlist_id, tracks):
    """Add tracks to the playlist"""
    sp.user_playlist_add_tracks(SPOTIFY_USER_ID, playlist_id, [track['id'] for track in tracks], position=None)


def main():
    date = get_date()
    playlist_id = create_new_playlist(date)
    songs_list, authors_list = get_tracks_data(date)
    tracks = search_tracks(songs_list, authors_list)
    add_tracks_to_playlist(playlist_id, tracks)
    

main()

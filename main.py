from bs4.element import NamespacedAttribute
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

CLIENTID = "Enter your Client ID from Spotify Developer here"
CLIENTSECRET = """Enter your Client Secret from Spotify Developer here"""

URL = "https://www.billboard.com/charts/hot-100/"

# get the year
year = input("Which year do you want to travel to? Type the data in this format YYYY:\n")
current_year = datetime.now().year
while year < 1950 or year > current_year:
    print("Sorry, that is not the right format")
    year = input("Which year do you want to travel to? Type the data in this format YYYY:\n")

# get the limit of songs from the user
limit = input("What is the Limit of songs per Month? (Max: 100)\n")
# if limit is more than 100 set it to 100
limit = 100 if int(limit) > 100 else int(limit)
# get the name the playlist should have
playlist_name = input("What should be the name of the playlist?\n")

# array to check if a song is duplicated
all_all_songs = []
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private", redirect_uri="http://example.com", client_id=CLIENTID, client_secret=CLIENTSECRET, show_dialog=True, cache_path="token.txt"))
user_id = sp.current_user()["id"]
# create the playlist with the userdefined name
playlist = sp.user_playlist_create(user=user_id, name=f"{playlist_name}", public=False)
# for every Month
for i in range(1, 13):
    # array for urls to the songs
    song_urls = []
    # song name in this month
    all_songs = []
    # corresponding artists to the songs
    all_artist = []
    # need to prefix a zero to month if it is less than 10
    if i < 10:
        response = requests.get(f"{URL}{year}-0{i}-28")
    else:
        response = requests.get(f"{URL}{year}-{i}-28")
    # get the text format from request object
    content = response.text
    # get the html with Beautifulsoup
    soup = BeautifulSoup(content, 'html.parser')
    # find the content for the songs in the html
    songs = soup.find_all(name='li', class_='o-chart-results-list__item')
    found_songs = 0
    for song in songs:
        # find the song name in the html
        song_name = song.find('h3', class_='c-title')
        # find the artist name in the html
        artist = song.find('span', class_='c-label')
        # if there is no song name or the song was already looked up continue
        if song_name is None or song_name.text in all_all_songs:
            continue
        # break the loop if the userdefined limit is reached
        if found_songs == limit:
            break
        # append everything to the corresponding array
        all_all_songs.append(song_name.text)
        all_songs.append(song_name.text)
        all_artist.append(artist.text)
        found_songs += 1
    print(len(all_artist))
    print(len(all_songs))
    for j, song in enumerate(all_songs):
        # search for the song with a substring of the artist
        if len(all_artist[i]) > 4:
            result = sp.search(q=f"artist:{all_artist[j][:4]} track:{song} year:{year}", type="track")
        else:
            result = sp.search(q=f"artist:{all_artist[j]} track:{song} year:{year}", type="track")
        print(song)
        # get the url of the song if none was found give feedback to user
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_urls.append(uri)
        except IndexError:
            print(f"{song} doesn't exits in Spotify. Skipped.")
    # add the songs to the playlist
    if len(song_urls) > 0:
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist["id"], tracks=song_urls)
    if i == 7:
        sleep(30)
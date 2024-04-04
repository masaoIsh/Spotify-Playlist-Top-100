import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

REDIRECT_URI = "https://example.com"
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
USERNAME = os.getenv("USERNAME")

# Remove specified values from a list
def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]


# Create a Spotify API Client
sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private",
        username=USERNAME,  # email might also work, I haven't tested it
    )
)
user = sp.current_user()
# print(user)
user_id = user["id"]

# results = sp.search(q="track:" + song_name, type="track")
# print(results['tracks']['items'][0]['album']['artists'][0]['uri'])

user_input = input("Enter a date in the format YYYY-MM-DD: ")
base_url = "https://www.billboard.com/charts/hot-100"
response = requests.get(f"{base_url}/{user_input}")
website_html = response.text
year = user_input.split("-")[0]

soup = BeautifulSoup(website_html, "html.parser")
song_tags = soup.select(selector="li h3", class_="c-title")

top_100_songs_names = soup.find_all(name="h3", class_="u-letter-spacing-0021", id="title-of-a-story")
top_100_songs_names = [song.text.strip() for song in top_100_songs_names]
top_100_songs_names = remove_values_from_list(top_100_songs_names, 'Songwriter(s):')
top_100_songs_names = remove_values_from_list(top_100_songs_names, 'Producer(s):')
top_100_songs_names = remove_values_from_list(top_100_songs_names, 'Imprint/Promotion Label:')

# song = top_100_songs_names[0]
# search_result = sp.search(q=f"track: {song} year: {year}", type="track")
# print(search_result['tracks']['items'][0]['uri'])

song_uris = []
for song in top_100_songs_names:
    search_result = sp.search(q=f"track: {song}", type="track")
    # print(search_result['tracks']['items'][0])
    if search_result is None:
        continue
    else:
        song_uri = search_result['tracks']['items'][0]['uri']
        song_uris.append(song_uri)

playlist_name = f"{user_input} Billboard 100"
playlist_result = sp.user_playlist_create(user=user_id, name=playlist_name, public=False,
                                          description=f"Top 100 songs from {user_input}!")
playlist_id = playlist_result['id']

sp.playlist_add_items(playlist_id=playlist_id, items=song_uris, position=None)

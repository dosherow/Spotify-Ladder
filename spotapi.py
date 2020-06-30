from datetime import datetime, date

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas_gbq

from playlists import country_Ids, electronic_Ids, indie_Ids, pop_Ids, rap_Ids, rnb_Ids


def daily_pull():

    # defining scopes and auth token and spotipy object variable to make requests to api
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    genres_cutoffs = [
        ("electronic", "02-24-2020", electronic_Ids),
        ("country", "03-02-2020", country_Ids),
        ("pop", "03-02-2020", pop_Ids),
        ("indie", "02-24-2020", indie_Ids),
        ("rap", "02-17-2020", rap_Ids),
        ("rnb", "03-02-2020", rnb_Ids),
    ]

    for genre, cut_off_date, playlist_ids in genres_cutoffs:
        pull_playlist(spotify, playlist_ids)

# creating nested artist object function to use artist_Id from playlist tracks loop and
# get followers, genres, and artist popularity metrics from each artist object.
def artist_obj(spotify, artist_Id):
    artist_info = spotify.artist(artist_Id)
    followers = artist_info["followers"]["total"]
    genres = artist_info["genres"]
    artist_pop = artist_info["popularity"]

    return {
        "followers": followers,
        "genres": genres,
        "artist_pop": artist_pop,
    }


def pull_playlist(spotify, playlist_ids):

    # starting loop through each playlist iteration from our playlist ids
    for playlist_id in playlist_ids:
        playlist_Obj = spotify.playlist(playlist_id[1])
        playlist_followers = playlist_Obj["followers"]["total"]
        spot_Playlists = spotify.playlist_tracks(playlist_id[1])
        # setting iteration variable to count position in chart
        iter = 1
        position = 0
        # all rows empty array to append all tracks in playlist to at end of playlist
        all_rows = []
        # starting loop to loop thru each row of playlist and grab artist name, artist ID, track name, track ID,
        # track popularity metric, release date, and added to date
        for chart in spot_Playlists["items"]:
            try:
                artist = chart["track"]["album"]["artists"][0]["name"]
                artist_Id = chart["track"]["album"]["artists"][0]["id"]
                artist_stats = artist_obj(spotify, artist_Id)
                followers = artist_stats.get("followers")
                genres = artist_stats.get("genres")
                artist_popularity = artist_stats.get("artist_pop")
                track = chart["track"]["name"]
                track_Id = chart["track"]["id"]
                pop = chart["track"]["popularity"]
                release_date = chart["track"]["album"]["release_date"]
                added_at = chart["added_at"]
                playlist_Name = playlist_id[0]
                d = date.today()
                # fixing api request error when metadata for release date is messed up
                if release_date is not None and release_date != "0000":
                    date_release_date = release_date = datetime.strptime(
                        release_date, "%Y-%m-%d"
                    )
                else:
                    release_date = release_date
                position += iter

                all_rows.append(
                    [
                        position,
                        artist,
                        artist_Id,
                        followers,
                        genres,
                        artist_popularity,
                        track,
                        track_Id,
                        pop,
                        release_date,
                        added_at,
                        playlist_Name,
                        playlist_followers,
                        d,
                    ]
                )

            # weird nonetype object not subscriptable error on random playlists at random tracks and positions, only fix
            # I've found thus far to continue if a chart item type is None
            except Exception:
                if chart is None:
                    continue

        df = pd.DataFrame(
            all_rows,
            columns=[
                "Position",
                "Artist",
                "Artist_Id",
                "Followers",
                "Genres",
                "Artist_Popularity",
                "Track",
                "Track_ID",
                "Track_Popularity",
                "Release_Date",
                "Add_Date",
                "Playlist_Name",
                "Playlist_Followers",
                "Date",
            ],
        )

        # ensuring data types are good for bigquery push

        df.dropna(subset=["Position"], inplace=True)
        df.dropna(subset=["Followers"], inplace=True)

        df['Position'] = df['Position'].astype(int)
        df['Followers'] = df['Followers'].astype(int)

        df["Release_Date"] = pd.to_datetime(df["Release_Date"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Add_Date"] = pd.to_datetime(df["Add_Date"])

        print(df)

        pandas_gbq.to_gbq(df,
                          "spotify_ladder.daily_pulls",
                          project_id="wired-method-203014",
                          if_exists="append")

if __name__ == "__main__":
    daily_pull()

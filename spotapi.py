import os
from os import environ
from datetime import datetime, date

import numpy as np
import pandas as pd
import spotipy
import spotipy.util as util
import pandas_gbq

from playlists import country_Ids, electronic_Ids, indie_Ids, pop_Ids, rap_Ids, rnb_Ids


def daily_pull():
    os.chdir(os.environ.get("LOCAL_DIRECTORY"))

    # defining scopes and auth token and spotipy object variable to make requests to api
    token = util.prompt_for_user_token(os.environ.get("SPOTIPY_USERNAME"))
    sp = spotipy.Spotify(auth=token)

    genres_cutoffs = [
        ("electronic", "02-24-2020", electronic_Ids),
        ("country", "03-02-2020", country_Ids),
        ("pop", "03-02-2020", pop_Ids),
        ("indie", "02-24-2020", indie_Ids),
        ("rap", "02-17-2020", rap_Ids),
        ("rnb", "03-02-2020", rnb_Ids),
    ]

    for genre, cut_off_date, playlist_ids in genres_cutoffs:
        xlsx_filename = get_xlsx_filename(genre)
        # csv_filename = get_csv_filename(genre)

        pull_playlist(sp, xlsx_filename, playlist_ids)
        # pivot(xlsx_filename, csv_filename, cut_off_date)


def get_xlsx_filename(genre):
    return genre + "Full" + datetime.now().strftime("%-m%d") + ".xlsx"


# def get_csv_filename(genre):
#     return genre + "PivotFull" + datetime.now().strftime("%-m%d") + ".csv"


# creating nested artist object function to use artist_Id from playlist tracks loop and
# get followers, genres, and artist popularity metrics from each artist object.
def artist_obj(sp, artist_Id):
    artist_info = sp.artist(artist_Id)
    followers = artist_info["followers"]["total"]
    genres = artist_info["genres"]
    artist_pop = artist_info["popularity"]

    return {
        "followers": followers,
        "genres": genres,
        "artist_pop": artist_pop,
    }


def pull_playlist(sp, filename, playlist_ids):

    # write playlist charts to each sheet in master
    writer_electronic = pd.ExcelWriter(filename, engine="xlsxwriter")
    # starting loop through each playlist iteration from our NMF array
    for playlist_id in playlist_ids:
        playlist_Obj = sp.playlist(playlist_id[1])
        playlist_followers = playlist_Obj["followers"]["total"]
        spot_Playlists = sp.playlist_tracks(playlist_id[1])
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

                artist_stats = artist_obj(sp, artist_Id)
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

        # new music friday playlists grabbing all of those values we want from each playlist
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

        # writing each playlist to single xlsx spreadsheet with each sheet name being unique new music friday title
        df.to_excel(
            writer_electronic, sheet_name=playlist_id[0], index=False, header=True
        )

    writer_electronic.save()
    writer_electronic.close()

    # reading in the excel output from above and merging all of the rows and columns into one table


# def pivot(xlsx_filename, csv_filename, cut_off_date):
#
#     electronic_df = pd.concat(
#         pd.read_excel(xlsx_filename, sheet_name=None), ignore_index=True,
#     )
#
#     # replacing blank release dates with null value
#     electronic_df["Release_Date"].replace("", np.nan, inplace=True)
#     # dropping null value rows for release date for bad metadata
#     electronic_df.dropna(subset=["Release_Date"], inplace=True)
#     # making release date column a datetime value
#     electronic_df["Release_Date"] = pd.to_datetime(electronic_df["Release_Date"])
#
#     # pivot table to create new columns for TRUE or FALSE for track appearing in each playlist we are grabbing
#     electronic_df["aux"] = 1
#     electronic_pivot = (
#         pd.pivot_table(
#             electronic_df,
#             index=[
#                 "Artist",
#                 "Track_Popularity",
#                 "Track",
#                 "Followers",
#                 "Genres",
#                 "Artist_Popularity",
#                 "Release_Date",
#                 "Date",
#             ],
#             columns=["Playlist_Name"],
#             aggfunc="count",
#             values="aux",
#         )
#         .fillna(0)
#         .astype(int)
#     )
#
#     # adding underscore to beg of columns for columns that start with number
#     # replacing white spaces with underscores
#     electronic_pivot.columns = electronic_pivot.columns.str.replace(" ", "_")
#     electronic_pivot.columns = electronic_pivot.columns.str.replace("&", "_")
#
#
#     # creating new column for total playlists, for each track
#     electronic_pivot["Total_Playlists"] = electronic_pivot.sum(axis=1)
#
#     # putting total playlists column at front
#     cols_full = [electronic_pivot.columns[-1]] + [
#         cols_full
#         for cols_full in electronic_pivot
#         if cols_full != electronic_pivot.columns[-1]
#     ]
#     electronic_pivot = electronic_pivot[cols_full]
#
#     electronic_pivot.reset_index(
#         level=[
#             "Artist",
#             "Date",
#             "Track_Popularity",
#             "Followers",
#             "Genres",
#             "Artist_Popularity",
#             "Release_Date",
#         ],
#         inplace=True,
#     )
#
#     ## making our range any row greater than the date above to query from total tracks in playlists
#     range = electronic_pivot["Release_Date"] > cut_off_date
#     # # putting the date range / cutoff together with the dataframe
#     electronic_pivot = electronic_pivot.loc[range]
#
#     # sorting table by total playlists track found in, from greatest to least
#     electronic_sorted_pivot = electronic_pivot.sort_values(
#         by="Total_Playlists", ascending=False
#     )
#
#     electronic_sorted_pivot = electronic_sorted_pivot.add_prefix("_")
#
#     ### CREATE NEW CSV HERE ALL PLAYLIST TRACKS WITHIN DATE CUTOFF ###
#
#     with open(csv_filename, "a") as f:
#         electronic_sorted_pivot.to_csv(f, header=True, index=True)



if __name__ == "__main__":
    daily_pull()

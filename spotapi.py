import os
import sys
import json
import spotipy
from datetime import datetime, date
from time import time
import re
import pandas as pd
import numpy as np
from playlists import rapIds, indieIds, electronicIds, popIds, countryIds, rnbIds, allIds, latinIds, portIds, frenchIds
import requests
# import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

os.chdir('/Users/drewharrison/Desktop/Playlists/week1Pop')


def pull_playlist():

    # write playlist charts to each sheet in master
    writer = pd.ExcelWriter('popFull327.xlsx', engine='xlsxwriter')

    # defining scopes and auth token and spotipy object variable to make requests to api
    scope = 'user-library-read user-read-recently-played user-top-read'
    username = 'littleshrow'

    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)

    # starting loop through each playlist iteration from our NMF array
    for popId in popIds:
        playlistObj = sp.playlist(popId[1])
        playlist_followers = playlistObj['followers']['total']
        spotPlaylists = sp.playlist_tracks(popId[1])
    # setting iteration variable to count position in chart
        iter = 1
        position = 0
    # all rows empty array to append all tracks in playlist to at end of playlist
        all_rows = []
    # starting loop to loop thru each row of playlist and grab artist name, artist ID, track name, track ID,
    # track popularity metric, release date, and added to date
        for chart in spotPlaylists['items']:
            try:
                artist = chart['track']['album']['artists'][0]['name']
                artist_Id = chart['track']['album']['artists'][0]['id']

                # creating nested artist object function to use artist_Id from playlist tracks loop and
                # get followers, genres, and artist popularity metrics from each artist object.
                def artist_obj(artist_Id):
                    artist_info = sp.artist(artist_Id)
                    followers = artist_info['followers']['total']
                    genres = artist_info['genres']
                    artist_pop = artist_info['popularity']

                    return {'followers': followers, 'genres': genres, 'artist_pop': artist_pop}
                artist_stats = artist_obj(artist_Id)
                followers = artist_stats.get('followers')
                genres = artist_stats.get('genres')
                artist_popularity = artist_stats.get('artist_pop')
                track = chart['track']['name']
                track_Id = chart['track']['id']
                pop = chart['track']['popularity']
                release_date = chart['track']['album']['release_date']
                added_at = chart['added_at']
                playlistName = popId[0]
                d = date.today()
                # fixing api request error when metadata for release date is messed up
                if release_date is not None and release_date != '0000':
                    date_release_date = release_date = datetime.strptime(release_date, '%Y-%m-%d')
                else:
                    release_date = release_date
                position += iter

                all_rows.append([position, artist, artist_Id, followers, genres, artist_popularity, track, track_Id,
                                     pop, release_date, added_at, playlistName, playlist_followers, d])

        # weird nonetype object not subscriptable error on random playlists at random tracks and positions, only fix
        # I've found thus far to continue if a chart item type is None
            except Exception:
                if chart is None:
                    continue

        # new music friday playlists grabbing all of those values we want from each playlist
        df = pd.DataFrame(all_rows, columns=['Position', 'Artist', 'Artist Id', 'Followers', 'Genres', 'Artist Popularity',
                                         'Track', 'Track ID', 'Track Popularity', 'Release Date', 'Add Date', 'Playlist Name', 'Playlist Followers',
                                             'Date'])

        print(df)

        # writing each playlist to single xlsx spreadsheet with each sheet name being unique new music friday title
        df.to_excel(writer, sheet_name=popId[0], index=False, header=True)

    writer.save()
    writer.close()

pull_playlist()

# reading in the excel output from above and merging all of the rows and columns into one table
def pivot():
    
    full_df = pd.concat(pd.read_excel('popFull327.xlsx', sheet_name=None), ignore_index=True)


    # replacing blank release dates with null value
    full_df['Release Date'].replace('', np.nan, inplace=True)
    # dropping null value rows for release date for bad metadata
    full_df.dropna(subset=['Release Date'], inplace=True)
    # making release date column a datetime value
    full_df['Release Date'] = pd.to_datetime(full_df['Release Date'])

    # pivot table to create new columns for TRUE or FALSE for track appearing in each playlist we are grabbing
    full_df['aux'] = 1
    full_pivot = pd.pivot_table(full_df, index=['Artist', 'Track Popularity', 'Track', 'Followers', 'Genres', 'Artist Popularity',
                                       'Release Date', 'Date'], columns=['Playlist Name'], aggfunc='count', values='aux').fillna(0).astype(int)
    
    # creating new column for total playlists, for each track
    full_pivot['Total Playlists'] = full_pivot.sum(axis=1)

    # putting total playlists column at front
    cols_full = [full_pivot.columns[-1]] + [cols_full for cols_full in full_pivot if cols_full != full_pivot.columns[-1]]
    full_pivot = full_pivot[cols_full]

    full_pivot.reset_index(level=['Artist', 'Date', 'Track Popularity', 'Followers', 'Genres', 'Artist Popularity',
                                  'Release Date'], inplace=True)

    # cutting off range of dates to only get us newest releases. change depending on start date of given genre 
    cut_off_date = '03-02-2020'
    # # making our range any row greater than the date above to query from total tracks in playlists
    range = (full_pivot['Release Date'] > cut_off_date)
    # # putting the date range / cutoff together with the dataframe
    full_pivot = full_pivot.loc[range]


    # sorting table by total playlists track found in, from greatest to least
    full_sorted_pivot = full_pivot.sort_values(by='Total Playlists', ascending=False)

    ### CREATE NEW CSV HERE ALL PLAYLIST TRACKS WITHIN DATE CUTOFF ###

    with open('popPivotFull327.csv', 'a') as f:
        full_sorted_pivot.to_csv(f, header=True, index=True)

pivot()

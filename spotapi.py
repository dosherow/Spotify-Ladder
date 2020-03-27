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

# starting loop through each playlist iteration from our Editorial array
# for editorial in editorials:
#     spotEditorials = sp.playlist_tracks(editorial[1])

    # setting iteration variable to count position in chart
    # iterator = 1
    # position = 0
    # all rows empty array to append all tracks in playlist to at end of playlist
    # all_rows = []

    # starting loop to loop thru each row of playlist and grab artist name, artist ID, track name, track ID,
    # track popularity metric, release date, and added to date
    # for chart in spotEditorials['items']:
    #     try:
    #         artist = chart['track']['album']['artists'][0]['name']
    #         artist_Id = chart['track']['album']['artists'][0]['id']
    #         track = chart['track']['name']
    #         track_Id = chart['track']['id']
    #         pop = chart['track']['popularity']
    #         release_date = chart['track']['album']['release_date']
    #         added_at = chart['added_at']
    #         if release_date is not None and release_date != '0000':
    #             date_release_date = release_date = datetime.strptime(release_date, '%Y-%m-%d')
    #         else:
    #             release_date = release_date
    #         position += iterator
    #         # appending all of the pulled data for each row to the empty array
    #         all_rows.append([position, artist, artist_Id, track, track_Id, pop, release_date, added_at])

        # weird nonetype object not subscriptable error on random playlists at random tracks and positions, only fix
        # I've found thus far to continue if a chart item type is None
        # except Exception:
        #     if chart is None:
        #         continue

    # editorial playlists creating table for each appended array and unique playlist before starting next iteration
    # of loop for next playlist in editorial array

    # df = pd.DataFrame(all_rows, columns=['Position', 'Artist', 'Artist Id', 'Track', 'Track ID', 'Track Popularity',
    #                                      'Release Date', 'Add Date'])

    # print(df)

    # creating a single excel output with a separate sheet for each unique playlist table
#     df.to_excel(writer2, sheet_name=editorial[0], index=False, header=True)
# writer2.save()
# writer2.close()

# reading in the excel output from above and merging all of the rows and columns into one table
def pivot():
    # new_df = pd.concat(pd.read_excel('rapFull221.xlsx', sheet_name=None), ignore_index=True)
    full_df = pd.concat(pd.read_excel('popFull327.xlsx', sheet_name=None), ignore_index=True)

# removing duplicates so that we have a list of all unique tracks that are on these playlists
# unique_df = new_df.drop_duplicates('Track ID')
# print(unique_df)

# new_df is merged dataset with all playlists in one table

# replacing blank release dates with null value
#     new_df['Release Date'].replace('', np.nan, inplace=True)
    full_df['Release Date'].replace('', np.nan, inplace=True)
# dropping null value rows for release date for bad metadata
#     new_df.dropna(subset=['Release Date'], inplace=True)
    full_df.dropna(subset=['Release Date'], inplace=True)
# making release date column a datetime value
#     new_df['Release Date'] = pd.to_datetime(new_df['Release Date'])
    full_df['Release Date'] = pd.to_datetime(full_df['Release Date'])

    # # cutting off range of dates to only get us newest releases. change weekly
#     cut_off_date = '02-17-2020'
# # making our range any row greater than the date above to query from total tracks in playlists
#     range = (new_df['Release Date'] > cut_off_date)
# # putting the date range / cutoff together with the dataframe
#     new_df = new_df.loc[range]
# pivot table to create new columns for TRUE or FALSE for track appearing in each playlist we are grabbing
#     new_df['aux'] = 1
    full_df['aux'] = 1
    # fin_df = pd.pivot_table(new_df, index=['Artist', 'Track Popularity', 'Track', 'Followers', 'Genres', 'Artist Popularity',
    #                                    'Release Date', 'Date'], columns=['Playlist Name'], aggfunc='count', values='aux').fillna(0).astype(int)
    full_pivot = pd.pivot_table(full_df, index=['Artist', 'Track Popularity', 'Track', 'Followers', 'Genres', 'Artist Popularity',
                                       'Release Date', 'Date'], columns=['Playlist Name'], aggfunc='count', values='aux').fillna(0).astype(int)
# creating new column for total playlists, for each track
#     fin_df['Total Playlists'] = fin_df.sum(axis=1)

    # full_pivot.drop(['TGIF', 'Lush Lofi', 'Fresh Finds', 'Butter', 'Silk Sheets', 'Focus Flow', 'Modus Mio',
    #                  'Deutschrap Brandneu', 'Hitradio', 'Wilde Herzen', 'BuzzStop', 'Top Hits Switzerland',
    #                  'Front Left', 'Get Popped!', 'Local Hype', 'Mellow Styles', 'PVNCHLNRS', 'Fresh Rap',
    #                  'Cloud Rap', 'Douces Vibes', 'Top Hits Workout', 'Its Lit', 'Vibes',
    #                  'The Slaylist', 'Liiit', 'Aura', 'Hits Hits Hits', 'Hot Hits DK',
    #                  'Certi', 'Reprise', 'Savage', 'Dar el Rol', 'Beats n Bars', 'Declasse', 'Flow', 'Hip Hop Party',
    #                  'Rap Mixtape', 'Laid Back Beats', 'Rap Skills', 'Frontline Japan', 'Coffee & Beats', 'The Drip',
    #                  'Believe The Hype', 'Smellir dagsins', 'Bilerappia', 'Hip-Hop Circle', 'New Hip-Hop and R&B',
    #                  'FNMNL', 'Back To Halls', 'Conscious', 'We Move'], axis=1, inplace=True)
    full_pivot['Total Playlists'] = full_pivot.sum(axis=1)

# putting total playlists column at front
#     cols = [fin_df.columns[-1]] + [col for col in fin_df if col != fin_df.columns[-1]]
#     fin_df = fin_df[cols]
    cols_full = [full_pivot.columns[-1]] + [cols_full for cols_full in full_pivot if cols_full != full_pivot.columns[-1]]
    full_pivot = full_pivot[cols_full]

    full_pivot.reset_index(level=['Artist', 'Date', 'Track Popularity', 'Followers', 'Genres', 'Artist Popularity',
                                  'Release Date'], inplace=True)
    # print(full_pivot)

    # cutting off range of dates to only get us newest releases. change weekly
    cut_off_date = '03-02-2020'
    # # making our range any row greater than the date above to query from total tracks in playlists
    range = (full_pivot['Release Date'] > cut_off_date)
    # # putting the date range / cutoff together with the dataframe
    full_pivot = full_pivot.loc[range]


## total playlists column, create new % from each region for total playlists to right



# sorting table by total playlists track found in, from greatest to least
#     sorted_df = fin_df.sort_values(by='Total Playlists', ascending=False)
    full_sorted_pivot = full_pivot.sort_values(by='Total Playlists', ascending=False)
    # print(full_sorted_pivot)

# creating new spreadsheet with merged tables as one table
# of only unique tracks so remove duplicates from merged table
    # change header to FALSE when appending new day

    # create same csv below, but with ALL tracks, no date cut off

    ### CREATE NEW CSV HERE ALL PLAYLIST TRACKS NO DATE CUTOFF ###

    with open('popPivotFull327.csv', 'a') as f:
        full_sorted_pivot.to_csv(f, header=True, index=True)

    # creating csv for only tracks within cut off date range from 194-222
    # change header to FALSE when appending new day
    # with open('rapPivot224.csv', 'a') as f:
    #     sorted_df.to_csv(f, header=True index=True)

pivot()

# def tracks_output():
#     writer2 = pd.ExcelWriter('tracks_outputfin.xlsx', engine='xlsxwriter')
#     tracks_df = pd.read_excel('final_outputUSA.csv')
#     tracks_df.to_excel(writer2, sheet_name=tracks_df['Track'], index=False, header=True)
#
#     writer2.save()
#     writer2.close()
#
# tracks_output()


# pick random 100-200 tracks to track over time with release date in past week

# segment genres from artist objects into umbrella genres based on various subgenres and set
# genre column to 1/2 genres for each artist/track. create sheet based on each genre to see
# how they correlate to playlists

# add new columns for metrics for each individual sheet playlist like avg's, std's, etc.

# frequency and overlap viz













# for chart2 in spotPlaylists2['items']:
#     artist = chart2['track']['album']['artists'][0]['name']
#     track = chart2['track']['name']
#     pop = chart2['track']['popularity']
#     release_date = chart2['track']['album']['release_date']
#     added_at = chart2['added_at']
#     if release_date is not None and release_date != '0000':
#         date_release_date = release_date = datetime.strptime(release_date, '%Y-%m-%d')
#         # print(date_release_date)
#         # print(date.today())
#         # print(type(date_release_date))
#         # age_of_track = date.today() - date_release_date
#         # print(age_of_track)
#     else:
#         release_date = release_date
#     position2 += iter2
#     # feat = re.split('\W', track)
#     # print(feat)
#     # print(pop)
#     all_rows2.append([position2, artist, track, pop, release_date, added_at])
#     track_final2 = [[position2, artist, track, pop, release_date, added_at]]
#     track_final2 = np.asarray(track_final2)
# df2 = pd.DataFrame(all_rows2, columns=['Position', 'Artist', 'Track', 'Track Popularity', 'Release Date', "Add Date"])
# print(df2)
# #
#
# with open('test.csv', 'a') as file:
#     file.write('test uk 2/7/20\n')
#     df2.to_csv(file, header=True, index=False)
#


# if token:
#     sp = spotipy.Spotify(auth=token)
#     results = sp.current_user_top_tracks(20,0,"short_term")
#     print("My Most Top Played Tracks:" + "\n")
#     for item in results['items']:
#         track = item['name']
#         print(track + ' - ' + )
#         # print(track + ' - ' + track['artists'][0]['name'])
# else:
#     print("Can't get token for", username)

## mine littleshrow

# erase cache and prompt for user permission
# try:
#     token = util.prompt_for_user_token(username)
# except:
#     os.remove(f".cach-{username}")
#     token = util.prompt_for_user_token(username)
#
# # create our spotifyObject
# sp = spotipy.Spotify(auth=token)

# print (json.dumps(VARIABLE, sort_keys=True, indent=4))
# prints json data in format we can read

# grab current user

# user = sp.current_user()
# print(json.dumps(user, sort_keys=True, indent=4))
#
# displayName = user['display_name']
# followers = user['followers']['total']
# savedTracks = user.current_user_top_tracks()
# print('My Saved Tracks:')
# for item in savedTracks['items']:
#     track = item['track']
#     print(track['name'] + ' - ' + track['artists'][0]['name'])
    # print(json.dumps(userTopTracks, sort_keys=True, indent=4))

# while True:
#
#     print()
#     print(">>> Welcome to Spotipy " + displayName + "!")
#     print(">>> You have " + str(followers) + " followers.")
#     print()
#     print("0 - Search for an artist")
#     print("1 - exit ")
#     print()
#     choice = input("Your choice: ")
#
#     # search for an artist
#     if choice == "0":
#         print()
#         searchQuery = input("OK, what's their name?: ")
#         print()
#
#         # get search results
#         searchResults = spotifyObject.search(searchQuery,1,0,"artist")
#         # print(json.dumps(searchResults, sort_keys=True, indent=4))
#
#         artist = searchResults['artists']['items'][0]
#         print(artist['name'])
#         print(str(artist['followers']['total']) + ' followers')
#         print()
#
#         artistID = artist['id']
#
#         # album and track details
#         trackURIs = []
#         trackArt = []
#         z = 0
#
#         # extract album data
#         albumResults = spotifyObject.artist_albums(artistID)
#         topTracks = spotifyObject.artist_top_tracks(artistID)
#         albumResults = albumResults['items']
#
#         print((artist['name']) + " Top Tracks: ")
#         for tracks in topTracks['tracks'][:10]:
#             print(tracks['name'])
#
#         for item in albumResults:
#             print("Album " + item['name'])
#             albumID = item['id']
#
#             # extract track data
#             trackResults = spotifyObject.album_tracks(albumID)
#             trackResults = trackResults['items']
#
#             for item in trackResults:
#                 print(str(z) + ": " + item['name'])
#                 trackURIs.append(item['uri'])
#                 z+=1
#             print()
#
#
#     if choice == "1":
#         break


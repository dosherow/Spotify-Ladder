# Spotify-Ladder

Notes on Pulling Playlists Each Day using spotapi.py file:

1) You will need to install spotipy which is a python wrapper for the Spotify Web API. 

2) Make sure your Spotify API Client ID, Client Secret, and Redirect URI are set as environment variables.

3) Switch littleshrow under username in 6 genre files for your username. 

4) Running spotapi.py file should give you 12 outputs, 6 xlsx files one for each genre daily with each playlist that is being tracked full chart in separate tabs, 6 csv files with pivot tables and sorted by tracks appearing on the most playlists per genre on a given day. All output files are saved under Playlists/all folder and file name changes dynamically based on date of pull. 
 

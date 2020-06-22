# Spotify-Ladder

## Requirements
* spotipy - a python wrapper for the Spotify Web API
* pandas
* numpy

## How to Run

1. Install requirements via requirements.txt 
1. Make sure your Spotify API Client ID, Client Secret, and Redirect URI are set as environment variables (see .env.example)
1. Switch littleshrow under username in 6 genre files for your username. 
1. Change output directory for files to whatever path you want on your local.
1. Running spotapi.py file should give you 12 outputs, 6 xlsx files one for each genre daily with each playlist that is being tracked full chart in separate tabs, 6 csv files with pivot tables and sorted by tracks appearing on the most playlists per genre on a given day. All output files are saved under Playlists/all folder and file name changes dynamically based on date of pull. 
 

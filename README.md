# Spotify-Ladder

Notes on Pulling Playlists Each Day using spotapi.py file:

1) You will need to install spotipy which is a python wrapper for the Spotify Web API. 

2) You will be prompted to provide client ID and client Secret when running the file that you shall get from Spotify Developer API site. You will also be prompted to provide a Redirect URI which you can make any URL. 

3) I have created a single folder to hold all of the dates outputs and inside that folder created 6 folders, 1 for each genre we are pulling for. When you pull a single genre at a time you should change the os.chdir to the folder of the given genre you are pulling for before the pull_playlist function. 

4) At the beginning of the pull_playlist function, you should change the date in the ExcelWriter file name to the current date. 

5) Under defining scopes, disregard the scope, but change username to your spotify username which aligns with your api developer account you signed up for. 

6) Each time you run the program, you will need to change the first for loop variable to the variable that aligns with the genre you are pulling. The variables are lists of spotify playlists with their names and id's and countries found in playlists.py file. You will also need to change this variable where popId[1] for playlistObj and for spotPlaylists variable each time you pull a different genre. Further down you need to change this variable where popId[0] for playlistName each time you pull a different genre. Same applies for the popId[0] for sheet_name on the df.to_excel line at the end of the pull_playlist function. 

7) For the pivot function, you need to read the same xlsx file you just wrote for each respective genre and make sure the date in the file name matches or else you will write a pivot table for a different date. On line 128, the cut_off_date should change as follows based on when we started pulling playlists of each genre to reflect the very beginning of tracks journeys: 
  Rap: '02-17-2020'
  Indie: '02-24-2020'
  Electronic: '02-24-2020'
  Pop: '03-02-2020'
  Country: '03-02-2020'
  R&B: '03-02-2020'
  
8) On line 140 remember to change file name to reflect genre pulling for and current date. 
 

from rap import rap_daily
from indie import indie_daily
from electronic import electronic_daily
from pop import pop_daily
from country import country_daily
from rnb import rnb_daily
import os

# choosing directory for output files
os.chdir("/Users/drewharrison/Desktop/Spotify-Ladder/Playlists/all")


# calling genre functions

rap_daily()
indie_daily()
electronic_daily()
pop_daily()
country_daily()
rnb_daily()
#!/usr/local/bin/python
from pathlib import Path
from PIL import Image
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
import stat
from configparser import ConfigParser
import platform
import imagehash
from datetime import datetime

config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
plexlibrary = (server["FILMSLIBRARY"])
ppath = (server["PLEXPATH"])
mpath = (server["MOUNTEDPATH"])
pbak = str.lower((options["POSTER_BU"]))
plex = PlexServer(baseurl, token)
films = plex.library.section(plexlibrary)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": Restore backup posters starting now")

for i in films.search():  
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png') 
    if backup == True:
        poster = newdir+'poster_bak.png'
        print(i.title)
        i.uploadPoster(filepath=poster)
        os.remove(poster)

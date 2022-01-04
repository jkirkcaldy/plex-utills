from PIL import Image, ImageFile
from plexapi.server import PlexServer
import plexapi
import numpy as np
import requests
import shutil
import os
import re
import imagehash
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
from tmdbv3api import TMDb, Search, Movie, Discover
from pymediainfo import MediaInfo
import json
from tautulli.api import RawAPI
import sys
print("Test running")
try:
    var = sys.argv[1]
    var2 = sys.argv[2]
except IndexError as e:
    print (e)
    print('you must enter your film library and a film title')
    
conn = sqlite3.connect('/config/app.db')
c = conn.cursor()
c.execute("SELECT * FROM plex_utills")
config = c.fetchall()

plex = PlexServer(config[0][1], config[0][2])
films = plex.library.section(var)

for i in films.search(title=var2):
    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
    tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
    resolution = i.media[0].videoResolution
    file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
    try:
        m = MediaInfo.parse(file, output='JSON')
        x = json.loads(m)
        print(x)
    except IndexError as e:
        print(e)
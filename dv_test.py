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

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    fileHandler = RotatingFileHandler(log_file, mode='w', maxBytes=100000, backupCount=5)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

setup_logger('plex-utills', r"/logs/script_log.log")
logger = logging.getLogger('plex-utills')

banner_4k = Image.open("app/img/4K-Template.png")
mini_4k_banner = Image.open("app/img/4K-mini-Template.png")
banner_hdr = Image.open("app/img/hdr-poster.png")
banner_dv = Image.open("app/img/dolby_vision.png")
banner_hdr10 = Image.open("app/img/hdr10.png")
chk_banner = Image.open("app/img/chk-4k.png")
chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
chk_hdr = Image.open("app/img/chk_hdr.png")
chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
chk_hdr10 = Image.open("app/img/chk_hdr10.png")
chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
banner_new_hdr = Image.open("app/img/hdr.png")
atmos = Image.open("app/img/atmos.png")
dtsx = Image.open("app/img/dtsx.png")
atmos_box = Image.open("app/img/chk_atmos.png")
dtsx_box = Image.open("app/img/chk_dtsx.png") 
size = (911,1367)
tv_size = (1280,720)
box= (0,0,911,100)
mini_box = (0,0,150,125)
hdr_box = (0,605,225,731)
a_box = (0,731,225,803)

tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2'
search = Search()
movie = Movie()
discover = Discover()

conn = sqlite3.connect('/config/app.db')
c = conn.cursor()
c.execute("SELECT * FROM plex_utills")
config = c.fetchall()

plex = PlexServer(config[0][1], config[0][2])
films = plex.library.section(var)
#films = plex.library.section("Films")

for i in films.search(title=var2):
    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
    tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
    resolution = i.media[0].videoResolution
    file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
    m = MediaInfo.parse(file, output='JSON')
    x = json.loads(m)
    #print(x)
    hdr_version = ""
    try:
        hdr_version = x['media']['track'][1]['HDR_Format_String']
    except (KeyError, IndexError):
        pass
    if "dolby" not in str.lower(hdr_version):
        try:
            hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
        except (KeyError, IndexError):
            try:
                hdr_version = x['media']['track'][1]['HDR_Format_Commercial_IfAny']
            except (KeyError, IndexError):
                pass
    audio = ""
    try:
        while True:
            for f in range(10):
                if 'Audio' in x['media']['track'][f]['@type']:
                    if 'Format_Commercial_IfAny' in x['media']['track'][f]:
                        audio = x['media']['track'][f]['Format_Commercial_IfAny']
                        if 'DTS' in audio:
                            if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                                audio = 'DTS:X'
                        break
                    elif 'Format' in x['media']['track'][f]:
                        audio = x['media']['track'][f]['Format']
                        break
            if audio != "":
                break
    except IndexError as e:
        print(e)
        pass
    print(i.title+" - "+audio+" - "+hdr_version)

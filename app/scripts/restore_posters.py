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

import logging

import sqlite3

logger = logging.getLogger('restore-posters')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def restore_posters():
    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])


    logger.info(" Restore backup posters starting now")

    for i in films.search():  
        newdir = os.path.dirname(re.sub(config[0][5], config[0][6], i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png') 
        if backup == True:
            poster = newdir+'poster_bak.png'
            logger.info(i.title+ 'Restored')
            i.uploadPoster(filepath=poster)
            os.remove(poster)
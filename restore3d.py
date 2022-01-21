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
import time
import unicodedata
import datetime
import sys

def setup_logger(logger_name, log_file):
    try:
        conn = sqlite3.connect('/config/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        config = c.fetchall()
        if config[0][36] == 1:
            loglevel = 'DEBUG'
        else:
            loglevel = 'INFO'
        c.close()
    except Exception:
        loglevel = 'INFO'
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s')
    fileHandler = RotatingFileHandler(log_file, mode='w', maxBytes=100000, backupCount=5)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(loglevel)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

setup_logger('plex-utills', r"/logs/script_log.log")
logger = logging.getLogger('plex-utills')
tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
search = Search()
movie = Movie()

var = sys.argv[1]
var2 = sys.argv[2]
def restore_posters3d(): 
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]
    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(var)
    banner_3d = Image.open("app/img/3D-Template.png")
    mini_3d_banner = Image.open("app/img/3D-mini-Template.png")
    chk_banner = Image.open("app/img/chk_3d_wide.png")
    chk_mini_banner = Image.open("app/img/chk-3D-mini.png")
    size = (911,1367)
    box= (0,0,911,100)
    mini_box = (0,0,301,268)
    logger.info("3D Posters: 3D poster script starting now.")  
    def restore():
        def restore_tmdb():
            logger.info("RESTORE: restoring posters from TheMovieDb")
            def get_tmdb_guid():
                g = str(i.guids)
                g = g[1:-1]
                g = re.sub(r'[*?:"<>| ]',"",g)
                g = re.sub("Guid","",g)
                g = g.split(",")
                f = filter(lambda a: "tmdb" in a, g)
                g = list(f)
                g = str(g[0])
                gv = [v for v in g if v.isnumeric()]
                g = "".join(gv)
                return g
            g = get_tmdb_guid()
            tmdb_search = movie.details(movie_id=g)
            logger.info(i.title)
            def get_poster(poster):
                r = requests.get(poster_url_base+poster, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open('tmdb_poster_restore.png', 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                        i.uploadPoster(filepath='tmdb_poster_restore.png')
                        os.remove('tmdb_poster_restore.png')
            try:
                poster = tmdb_search.poster_path
                get_poster(poster) 
            except TypeError:
                logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                pass
        def restore_from_local():
            logger.info("restoring posters from Local Backups")
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            poster = newdir+'poster_bak.png'
            backup = os.path.exists(poster)
            if backup == True:
                logger.info('Backup=true')
                logger.info(poster)
                i.uploadPoster(filepath=poster)
                logger.info(i.title+ ' Restored')
            else:
                poster = newdir+' poster_bak.png'
                backup = os.path.exists(poster)
                if backup == True:
                    i.uploadPoster(filepath=poster)
                    logger.info(i.title+ ' Restored')
                else:
                    logger.error('Can not find a backup for this poster')
            
        if var2 == 'tmdb':
            restore_tmdb()
        else:
            restore_from_local()
    
    def check_for_mini():
        background = Image.open('/tmp/poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(mini_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_mini_banner)
        logger.info('checking for mini')
        cutoff= 25
        if hash0 - hash1 < cutoff:
            logger.info('3D Posters: Mini 3D banner exists, restoring')
            restore()
        #elif config[0][17] == 1:
        #    add_mini_banner()
        #else:
        #    add_banner()       
    def check_for_banner():
        background = Image.open('/tmp/poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_banner)
        cutoff= 25
        if hash0 - hash1 < cutoff:
            logger.info('3D Posters: 3D banner exists, restoring')
            restore()
        else:
            check_for_mini()  
    def get_poster():
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        if img.status_code == 200:
            img.raw.decode_content = True
            filename = "/tmp/poster.png"
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img.raw, f)
            
        else:
            logger.warning("Restore 3D Posters: "+films.title+" cannot find the poster for this film")   
    for i in films.search():
        i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
        logger.info(i.title)
        try:
            get_poster()
            check_for_banner()
        except FileNotFoundError:
            logger.error("3D Posters: "+films.title+" The 3D poster for this film could not be restored.")
            continue
    logger.info("3D Posters: 3D Poster Script has finished.")
    c.close()
restore_posters3d()
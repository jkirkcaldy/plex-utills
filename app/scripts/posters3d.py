
from PIL import Image
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
import imagehash
import logging
import sqlite3


logger = logging.getLogger('3D-posters')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Do not edit these, use the config file to make any changes

def posters3d():
    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][4])

    banner_3d = Image.open("./app/img/3D-Template.png")
    mini_3d_banner = Image.open("./app/img/3D-mini-Template.png")

    chk_banner = Image.open("./app/img/chk_3d_wide.png")
    chk_mini_banner = Image.open("./app/img/chk-3D-mini.png")

    size = (911,1367)
    box= (0,0,911,100)
    mini_box = (0,0,301,268)

    logger.info("3D poster script starting now.")  

    def check_for_mini():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(mini_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_mini_banner)
        cutoff= 15
        if hash0 - hash1 < cutoff:
            logger.info('Mini 3D banner exists, moving on...')
        else:    
            if config[0][17] == 1:
                add_mini_banner()
            else:
                add_banner()       

    def check_for_banner():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_banner)
        cutoff= 5
        if hash0 - hash1 < cutoff:
            logger.info('3D banner exists, moving on...')
        else:
            check_for_mini()  

    def add_banner():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        background.paste(banner_3d, (0, 0), banner_3d)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")

    def add_mini_banner():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        background.paste(mini_3d_banner, (0, 0), mini_3d_banner)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")        

    def get_poster():
        newdir = os.path.dirname(re.sub(config[0][5], config[0][6], i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        filename = "poster.png"

        if img.status_code == 200:
            img.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img.raw, f)
            if config[0][12] == 1: 
                if backup == True: 
                    #open backup poster to compare it to the current poster. If it is similar enough it will skip, if it's changed then create a new backup and add the banner. 
                    poster = os.path.join(newdir, 'poster_bak.png')
                    b_check1 = Image.open(filename)
                    b_check = Image.open(poster)
                    b_hash = imagehash.average_hash(b_check)
                    b_hash1 = imagehash.average_hash(b_check1)
                    cutoff = 5
                    if b_hash - b_hash1 < cutoff:    
                        logger.info('Backup File Exists, Skipping')
                    else:
                        os.remove(poster)
                        logger.info('Creating a backup file')
                        dest = shutil.copyfile(filename, newdir+'poster_bak.png')
                else:        
                    logger.info('Creating a backup file')
                    dest = shutil.copyfile(filename, newdir+'poster_bak.png')
        else:
            logger.warning("cannot find the poster for this film")   

    for i in films.search():
        logger.info(i.title)
        try:
            get_poster()
            check_for_banner()
        except FileNotFoundError:
            logger.error("The 3D poster for this film could not be created.")
            continue         

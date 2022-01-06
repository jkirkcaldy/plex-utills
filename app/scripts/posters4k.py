from pathlib import Path
from PIL import Image, ImageChops
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
import imagehash
import logging

import sqlite3

logger = logging.getLogger('4K-posters')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def posters4k():


    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()




    banner_4k = Image.open("./app/img/4K-Template.png")
    mini_4k_banner = Image.open("./app/img/4K-mini-Template.png")
    banner_hdr = Image.open("./app/img/hdr-poster.png")
    chk_banner = Image.open("./app/img/chk-4k.png")
    chk_mini_banner = Image.open("./app/img/chk-mini-4k2.png")
    chk_hdr = Image.open("./app/img/chk_hdr.png")
    size = (911,1367)
    box= (0,0,911,100)
    mini_box = (0,0,150,125)
    hdr_box = (0,611,215,720)
    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])


    logger.info(": 4k HDR poster script starting now.")

    def check_for_mini():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(mini_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_mini_banner)
        cutoff= 10
        if hash0 - hash1 < cutoff:
            logger.info('Mini 4k banner exists, moving on')
        elif config[0][14] == 1:
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
            logger.info('4K banner exists, moving on')
        else:
            check_for_mini()   
    def add_banner():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        background.paste(banner_4k, (0, 0), banner_4k)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")
    def add_mini_banner():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")
    def add_hdr():
        background = Image.open('poster.png')
        background = background.resize(size,Image.ANTIALIAS)
        backgroundchk = background.crop(hdr_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(chk_hdr)
        cutoff= 5
        if hash0 - hash1 < cutoff:
            logger.info('HDR banner exists, moving on')
            print('HDR banner exists, moving on...')
        else:
            background.paste(banner_hdr, (0, 0), banner_hdr)
            background.save('poster.png')
            i.uploadPoster(filepath="poster.png")
    def get_poster():
        newdir = os.path.dirname(re.sub(config[0][5], config[0][6], i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        if img.status_code == 200:
            img.raw.decode_content = True
            filename = "poster.png"
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
                    cutoff = 10
                    if b_hash - b_hash1 < cutoff:
                        logger.info('Backup file exists, skipping')    
                    else:
                        #Check to see if the poster has a 4k Banner
                        background = Image.open(filename)
                        background = background.resize(size,Image.ANTIALIAS)
                        backgroundchk = background.crop(box)
                        hash0 = imagehash.average_hash(backgroundchk)
                        hash1 = imagehash.average_hash(chk_banner)
                        cutoff= 5
                        if hash0 - hash1 < cutoff:
                            logger.info('Poster has 4k Banner, Skipping Backup')
                            #print(Fore.LIGHTRED_EX, 'Poster has 4k banner, skipping backup', Fore.RESET)
                        else:
                            #Check if the poster has a mini 4k banner
                            background = Image.open(filename)
                            background = background.resize(size,Image.ANTIALIAS)
                            backgroundchk = background.crop(mini_box)
                            hash0 = imagehash.average_hash(backgroundchk)
                            hash1 = imagehash.average_hash(chk_mini_banner)
                            cutoff= 10
                            if hash0 - hash1 < cutoff: 
                                logger.info('Poster has Mini 4k Banner, Skipping Backup')
                            else:
                                logger.info('New poster detected, creating new Backup') 
                                os.remove(poster)
                                logger.info('Check passed, creating a backup file')
                                dest = shutil.copyfile(filename, newdir+'poster_bak.png')
                else:        
                    logger.info('Creating a backup file')
                    dest = shutil.copyfile(filename, newdir+'poster_bak.png')
        else:
            logger.warning(films.title+ 'cannot find the poster for this film')

    def poster_4k_hdr():
        logger.info(i.title + '4K HDR')    
        get_poster()
        check_for_banner() 
        add_hdr()                                  
        os.remove('poster.png')              
    def poster_4k():   
        logger.info(i.title + '4K Poster')
        get_poster()
        check_for_banner()                             
        os.remove('poster.png')   
    def poster_hdr():
        logger.info(i.title + 'HDR Poster')
        get_poster() 
        add_hdr()                                  
        os.remove('poster.png')      


    if config[0][15] == 1:
        for i in films.search(resolution="4k", hdr=False):
            try:
                poster_4k()
            except FileNotFoundError:
                logger.error(films.title+" The 4k poster for this film could not be created.")
                continue    
        for i in films.search(resolution="4k", hdr=True):
            try:
                poster_4k_hdr()
            except FileNotFoundError:
                logger.error(films.title+" The 4k HDR poster for this film could not be created.")
                continue
        for i in films.search(resolution="1080,720", hdr=True):
            try:
                poster_hdr()
            except FileNotFoundError:
                logger.error(films.title+" The HDR poster for this film could not be created.")
                continue
    else:
        logger.info('Creating 4K posters only')
        print('Creating 4k posters only')
        for i in films.search(resolution="4k"):
            try:
                poster_4k()
            except FileNotFoundError:
                logger.error(films.title+" The 4k poster for this film could not be created.")
                continue    
      
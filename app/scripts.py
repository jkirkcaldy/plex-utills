
from PIL import Image, ImageFile
from plexapi import config
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
import imagehash
import logging
import sqlite3
from tmdbv3api import TMDb, Search





logger = logging.getLogger('Plex-Utills')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
ImageFile.LOAD_TRUNCATED_IMAGES = True
tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/w600_and_h900_bestv2'
search = Search()

def setup_helper():
    def create_table():
        shutil.copy('app/static/default_db/default_app.db', 'app/app.db')
    def continue_setup():
        conn = sqlite3.connect('app/app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM plex_utills")
        config = c.fetchall()
    
        logger.info("Setup Helper: Going though the setup helper.")
    
        
        
        try:
            plex = PlexServer(config[0][1], config[0][2])
            films = plex.library.section(config[0][3])
            media_location = films.search()
            filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
            plexpath = '/'+filepath.split('/')[1]
    
            c.execute("UPDATE plex_utills SET plexpath = '"+plexpath+"' WHERE ID = 1;")
            conn.commit()
            c.close()
            logger.info("Setup Helper: Your plexpath has been changed to "+plexpath)
            
        except OSError as e:
            if e.errno == 111: 
                logger.warning("Setup Helper: Cannont connect to your plex server, this may be because it is the first run and you haven't changed the config yet.")

    def table_check():
        database = os.path.exists('app/app.db')
        if database == True:
            continue_setup()
        else:
            create_table()
    table_check()

def posters4k():
    
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    if config[0][13] == 1:
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
        size = (911,1367)
        tv_size = (1280,720)
        box= (0,0,911,100)
        mini_box = (0,0,150,125)
        hdr_box = (0,611,215,720)
        plex = PlexServer(config[0][1], config[0][2])
        
        
        logger.info("4k Posters: 4k HDR poster script starting now.")
        def check_for_mini():
            background = Image.open('poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(mini_box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_mini_banner)
            cutoff= 10
            if hash0 - hash1 < cutoff:
                logger.info('4k Posters: Mini 4k banner exists, moving on')
            else:    
                if config[0][14] == 1:
                    add_mini_banner()
                else:
                    add_banner()  

        def check_for_mini_tv():
            background = Image.open('poster.png')
            background = background.resize(tv_size,Image.ANTIALIAS)
            backgroundchk = background.crop(mini_box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_mini_banner)
            cutoff= 10
            if hash0 - hash1 < cutoff:
                logger.info('4k Posters: Mini 4k banner exists, moving on')
            else:    
                add_mini_tv_banner()
        def add_mini_tv_banner():
            background = Image.open('poster.png')
            background = background.resize(tv_size,Image.ANTIALIAS)
            background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
            background.save('poster.png')
            i.uploadPoster(filepath="poster.png")
        def check_for_banner():
            background = Image.open('poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_banner)
            cutoff= 5
            if hash0 - hash1 < cutoff:
                logger.info('4k Posters: 4K banner exists, moving on')
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
        def add_new_hdr():
            background = Image.open('poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(hdr_box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_new_hdr)
            hash2 = imagehash.average_hash(chk_dolby_vision)
            hash3 = imagehash.average_hash(chk_hdr10)
            hash4 = imagehash.average_hash(chk_hdr)
            cutoff= 10
            name = str.lower(i.media[0].parts[0].file)

            if "dolby" and "vision" in name:
                if hash0 - hash2 < cutoff:
                    logger.info("HDR Banner: "+i.title+" dolby-vision poster exists moving on")
                else:
                    logger.info("HDR Banner: "+i.title+" adding dolby-vision hdr banner")
                    background.paste(banner_dv, (0, 0), banner_dv)
                    background.save('poster.png')
                    i.uploadPoster(filepath="poster.png")
            elif "hdr10" in name:
                if hash0 - hash3 < cutoff:
                    logger.info("HDR Banner: "+i.title+" hdr10 banner exists")
                else:
                    logger.info("HDR Banner: "+i.title+" adding HDR 10 banner now")
                    background.paste(banner_hdr10, (0, 0), banner_hdr10)
                    background.save('poster.png')
                    i.uploadPoster(filepath="poster.png")
            else:
                if hash0 - hash1 < cutoff:
                    logger.info("HDR Banner: "+i.title+' 4k Posters: HDR banner exists, moving on')
                else:
                    logger.info("HDR Banner: "+i.title+" adding hdr banner now")
                    background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
                    background.save('poster.png')
                    i.uploadPoster(filepath="poster.png")            

                    if "dolby" and "vision" in name:
                        if hash0 - hash2 < cutoff:
                            logger.info("HDR Banner: "+i.title+" dolby-vision poster exists moving on")
                        else:
                            logger.info("HDR Banner: "+i.title+" adding dolby-vision hdr banner")
                            background.paste(banner_dv, (0, 0), banner_dv)
                            background.save('poster.png')
                            i.uploadPoster(filepath="poster.png")
                    elif "hdr10" in name:
                        if hash0 - hash3 < cutoff:
                            logger.info("HDR Banner: "+i.title+" hdr10 banner exists")
                        else:
                            logger.info("HDR Banner: "+i.title+" adding HDR 10 banner now")
                            background.paste(banner_hdr10, (0, 0), banner_hdr10)
                            background.save('poster.png')
                            i.uploadPoster(filepath="poster.png")
                    else:
                        if hash0 - hash1 < cutoff:
                            logger.info("HDR Banner: "+i.title+' 4k Posters: HDR banner exists, moving on')
                        else:
                            logger.info("HDR Banner: "+i.title+" adding hdr banner now")
                            background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
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
                logger.info('HDR Banner: '+i.title+' HDR banner exists, moving on...')
            else:
                background.paste(banner_hdr, (0, 0), banner_hdr)
                background.save('poster.png')
                i.uploadPoster(filepath="poster.png")            
        def check_for_old_banner(): 
            background = Image.open('poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(hdr_box)
            hash0 = imagehash.average_hash(backgroundchk)   
            hash4 = imagehash.average_hash(chk_hdr)
            cutoff= 5
            if hash0 - hash4 < cutoff:
                logger.info(i.title+" has old hdr banner")
                for a in i:
                    newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
                    backup = os.path.exists(newdir+'poster_bak.png') 
                    if backup == True:
                        poster = newdir+'poster_bak.png'
                        logger.info(i.title+ ' Restored from local files')
                        i.uploadPoster(filepath=poster)
                        os.remove(poster)
                    else:
                        logger.info(i.title, i.year)
                        tmdb_search = search.movies({"query": i.title, "year": i.year})
                        def get_poster_link():
                            for r in tmdb_search:
                                poster = r.poster_path
                                return poster
                        def get_poster(poster):
                            r = requests.get(poster_url_base+poster, stream=True)
                            
                            if r.status_code == 200:
                                r.raw.decode_content = True
                                with open('poster.png', 'wb') as f:
                                    shutil.copyfileobj(r.raw, f)
                                    i.uploadPoster(filepath='poster.png')
                                    #os.remove('poster.png')
                                    logger.info(i.title+" Restored from TMDb")
                        try:
                            poster = get_poster_link()  
                            get_poster(poster) 
                        except TypeError:
                            logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                            continue
                        
        def get_poster():
            newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
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
                        cutoff = 10
                        if b_hash - b_hash1 < cutoff:
                            logger.info('4k Posters: Backup file exists, skipping')    
                        else:
                            #Check to see if the poster has a 4k Banner
                            background = Image.open(filename)
                            background = background.resize(size,Image.ANTIALIAS)
                            backgroundchk = background.crop(box)
                            hash0 = imagehash.average_hash(backgroundchk)
                            hash1 = imagehash.average_hash(chk_banner)
                            cutoff= 5
                            if hash0 - hash1 < cutoff:
                                logger.info('4k Posters: Poster has 4k Banner, Skipping Backup')
                            else:
                                #Check if the poster has a mini 4k banner
                                background = Image.open(filename)
                                background = background.resize(size,Image.ANTIALIAS)
                                backgroundchk = background.crop(mini_box)
                                hash0 = imagehash.average_hash(backgroundchk)
                                hash1 = imagehash.average_hash(chk_mini_banner)
                                cutoff= 10
                                if hash0 - hash1 < cutoff: 
                                    logger.info('4k Posters: Poster has Mini 4k Banner, Skipping Backup')
                                else:
                                    logger.info('4k Posters: New poster detected, creating new Backup') 
                                    os.remove(poster)
                                    logger.info('4k Posters: Check passed, creating a backup file')
                                    dest = shutil.copyfile(filename, newdir+'poster_bak.png')
                    else:        
                        logger.info('4k Posters: Creating a backup file')
                        dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            else:
                logger.warning("4k Posters: "+films.title+ 'cannot find the poster for this film')
        def get_TVposter():   
            newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
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
                        cutoff = 10
                        if b_hash - b_hash1 < cutoff:    
                            logger.info('4k Posters: Backup file exists, skipping')
                        else:                              
                            #Check if the poster has a mini 4k banner
                            background = Image.open(filename)
                            background = background.resize(size,Image.ANTIALIAS)
                            backgroundchk = background.crop(mini_box)
                            hash0 = imagehash.average_hash(backgroundchk)
                            hash1 = imagehash.average_hash(chk_mini_banner)
                            cutoff= 10
                            if hash0 - hash1 < cutoff: 
                                logger.info('4k Posters: Poster has Mini 4k Banner, Skipping Backup')
                            else:
                                logger.info('4k Posters: New poster detected, creating new Backup') 
                                os.remove(poster)
                                logger.info('4k Posters: Check passed, creating a backup file')
                                dest = shutil.copyfile(filename, newdir+'poster_bak.png')
                    else:        
                        logger.info('4k Posters: Creating a backup file')
                        dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            
            else:
                logger.info("4k Posters: "+films.title+" cannot find the poster for this Episode")


        def poster_4k_hdr():
            logger.info(i.title + ' 4K HDR')    
            get_poster()
            if config[0][28] == 1:
                check_for_old_banner()
                add_new_hdr()
            else:
                add_hdr()          
            check_for_banner()                     
            os.remove('poster.png')              
        def poster_4k():   
            logger.info(i.title + ' 4K Poster')
            get_poster()
            check_for_banner()                             
            os.remove('poster.png')   
        def poster_hdr():
            logger.info(i.title + ' HDR Poster')
            get_poster() 
            if config[0][28] == 1:
                check_for_old_banner()
                add_new_hdr()
            else:
                add_hdr()                                          
            os.remove('poster.png')      
    def posterTV_4k():   
        logger.info(i.title + " 4K Poster")
        get_TVposter()
        check_for_mini_tv()                             
        os.remove('poster.png') 
    if config[0][24] == 1 and config[0][3] != 'None':
        films = plex.library.section(config[0][3])
        if config[0][15] == 1:
            for i in films.search(resolution="4k", hdr=False):
                try:
                    poster_4k()
                except FileNotFoundError:
                    logger.error("4k Posters: "+films.title+" The 4k poster for this film could not be created.")
                    continue    
            for i in films.search(resolution="4k", hdr=True):
                try:
                    poster_4k_hdr()
                except FileNotFoundError:
                    logger.error("4k Posters: "+films.title+" The 4k HDR poster for this film could not be created.")
                    continue
            for i in films.search(resolution="1080,720", hdr=True):
                try:
                    poster_hdr()
                except FileNotFoundError:
                    logger.error("4k Posters: "+films.title+" The HDR poster for this film could not be created.")
                    continue
        else:
            logger.info('4k Posters: Creating 4K posters only')
            for i in films.search(resolution="4k"):
                try:
                    poster_4k()
                except FileNotFoundError:
                    logger.error("4k Posters: "+films.title+" The 4k poster for this film could not be created.")
                    continue        
    if config[0][23] == 1 and config[0][22] != 'None':
        tv = plex.library.section(config[0][22])
        for i in tv.searchEpisodes(resolution="4k"):
            try:
                posterTV_4k()
            except FileNotFoundError:
                logger.error("4k Posters: "+tv.title+" The 4k poster for this episode could not be created")          
    logger.info("4k Posters: 4K/HDR Poster Script has finished.")

def posters3d(): 
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    if config[0][16] == 1:
        plex = PlexServer(config[0][1], config[0][2])
        films = plex.library.section(config[0][4])

        banner_3d = Image.open("app/img/3D-Template.png")
        mini_3d_banner = Image.open("app/img/3D-mini-Template.png")

        chk_banner = Image.open("app/img/chk_3d_wide.png")
        chk_mini_banner = Image.open("app/img/chk-3D-mini.png")

        size = (911,1367)
        box= (0,0,911,100)
        mini_box = (0,0,301,268)

        logger.info("3D Posters: 3D poster script starting now.")  

        def check_for_mini():
            background = Image.open('poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(mini_box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_mini_banner)
            cutoff= 15
            if hash0 - hash1 < cutoff:
                logger.info('3D Posters: Mini 3D banner exists, moving on...')
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
                logger.info('3D Posters: 3D banner exists, moving on...')
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
            newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
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
                            logger.info('3D Posters: Backup File Exists, Skipping')
                        else:
                            os.remove(poster)
                            logger.info('3D Posters: Creating a backup file')
                            dest = shutil.copyfile(filename, newdir+' poster_bak.png')
                    else:        
                        logger.info('3D Posters: Creating a backup file')
                        dest = shutil.copyfile(filename, newdir+' poster_bak.png')
            else:
                logger.warning("3D Posters: "+films.title+" cannot find the poster for this film")   

        for i in films.search():
            logger.info(i.title)
            try:
                get_poster()
                check_for_banner()
            except FileNotFoundError:
                logger.error("3D Posters: "+films.title+" The 3D poster for this film could not be created.")
                continue
        logger.info("3D Posters: 3D Poster Script has finished.")

def restore_posters():
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    tmdb.api_key = config[0][25]

    logger.info("Restore-posters: Restore backup posters starting now")
    if config[0][26] == 0:
        logger.info("RESTORE: restoring posters from local backups")
    else:
        logger.info("RESTORE: restoring posters from TMDB")
    for i in films.search():  
        if config[0][26] == 0:
            newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png') 
            if backup == True:
                poster = newdir+'poster_bak.png'
                logger.info(i.title+ ' Restored')
                i.uploadPoster(filepath=poster)
                os.remove(poster)
        elif config[0][26] == 1:
            tmdb_search = search.movies({"query": i.title, "year": i.year})
            logger.info(i.title)
            def get_poster_link():
                for r in tmdb_search:
                    poster = r.poster_path
                    return poster
            def get_poster(poster):
                r = requests.get(poster_url_base+poster, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open('tmdb_poster_restore.png', 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                        i.uploadPoster(filepath='tmdb_poster_restore.png')
                        os.remove('tmdb_poster_restore.png')
            try:
                poster = get_poster_link()
            
                get_poster(poster) 
            except TypeError:
                logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                continue

def pixar():
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    if config[0][19] == 1:
        plex = PlexServer(config[0][1], config[0][2])
        movies_section = plex.library.section(config[0][3])
        added = movies_section.search(sort='titleSort')

        logger.info("Collections: Pixar Collection script starting now")

        for movie in added:
            try:
                if "Pixar" in movie.studio:
                    movie.addCollection('Pixar')
                    logger.info(movie.title+" "+movie.studio)
            # Skip movie if there is no studio info
            except TypeError:
                continue
        logger.info("Collections: Pixar Script has finished.")

def disney():
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    if config[0][18] == 1:
        plex = PlexServer(config[0][1], config[0][2])
        movies_section = plex.library.section(config[0][3])
        added = movies_section.search(sort='titleSort')

        logger.info("Collections: Disney Collection script starting now")

        for movie in added:
            try:
                if "Disney" in movie.studio:
                    movie.addCollection('Pixar')
                    logger.info(movie.title+" "+ movie.studio)
            # Skip movie if there is no studio info
            except TypeError:
                continue  
        logger.info("Collections: Disney Script has finished.")

def hide4k():
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    if config[0][20] == 1:

        plex = PlexServer(config[0][1], config[0][2])
        films = plex.library.section(config[0][3])


        logger.info("Hide-4K: Hide 4k films script starting now")

        
        added = films.search(resolution='4k', sort='addedAt')
        b = films.search(label='untranscodable', sort='addedAt')

        for movie in added:
            resolutions = {m.videoResolution for m in movie.media}
            if len(resolutions) < 2 and '4k' in resolutions:
                if config[0][21] == 0:
                    movie.addLabel('Untranscodable')   
                    logger.info("Hide-4K: "+movie.title+' has only 4k avaialble, setting untranscodable' )
                elif config[0][21] == 1:
                    logger.info('Hide-4K: Sending '+ movie.title+ ' to be transcoded')
                    movie.optimize(deviceProfile="Android", videoQuality=10)

        for movie in b:
            resolutions = {m.videoResolution for m in movie.media}
            if len(resolutions) > 1 and '4k' in resolutions:
                movie.removeLabel('Untranscodable')
                logger.info("Hide-4K: "+movie.title+ ' removing untranscodable label')
        logger.info("Hide-4K: Hide 4K Script has finished.")

def migrate():
    from configparser import ConfigParser
    config_object = ConfigParser()
    config_object.read("config/config.ini")
    server = config_object["PLEXSERVER"]
    schedules = config_object["SCHEDULES"]
    options = config_object["OPTIONS"]

    baseurl = (server["PLEX_URL"])
    token = (server["TOKEN"])

    plexlibrary = (server["FILMSLIBRARY"])
    library3d = (server["3D_Library"])

    hdr_4k_posters = str.lower((options["4k_hdr_posters"]))
    poster_3d = str.lower((options["3D_posters"]))
    Disney = str.lower((options["Disney"]))
    Pixar = (str.lower(options["Pixar"]))
    hide_4k = str.lower((options["hide_4k"]))
    pbak = str.lower((options["POSTER_BU"]))
    HDR_BANNER = str.lower((options["HDR_BANNER"]))
    optimise = str.lower((options["transcode"]))
    mini_4k = str.lower((options["mini_4k"]))
    mini_3d = str.lower((options["mini_3D"]))

    t1 = (schedules["4k_poster_schedule"])
    t2 = (schedules["disney_schedule"])
    t3 = (schedules["pixar_schedule"])
    t4 = (schedules["hide_poster_schedule"])
    t5 = (schedules["3d_poster_schedule"])

    if t1 == '':
        t1 = '00:00'
    if t2 == '':
        t2 = '00:00'
    if t3 == '':
        t3 = '00:00'
    if t4 == '':
        t4 = '00:00'
    if t5 == '':
        t5 = '00:00'                            

    if mini_4k == 'true':
        mini4k = 1
    else:
        mini4k = 0
    if hdr_4k_posters == 'true':
        posters4k = 1 
    else:
        posters4k = 0
    if HDR_BANNER == 'true':
        hdr = 1
    else:
        hdr = 0
    if poster_3d == 'true':
        posters3d = 1
    else:
        posters3d = 0
    if mini_3d == 'true':
        mini3d = 1
    else:
        mini3d = 0
    if pbak == 'true':
        backup = 1
    else:
        backup = 0
    if hide_4k == 'true':
        hide4k = 1
    else:
        hide4k = 0
    if optimise == 'true':
        transcode = 1
    else:
        transcode = 0
    if Disney == 'true':
        disney = 1
    else:
        disney = 0
    if Pixar == 'true':
        pixar = 1
    else:
        pixar = 0
    
    conn = sqlite3.connect('app/app.db')
    
    def update_config(conn, old_config):
        
        
        sql_update = """
            UPDATE plex_utills
            SET plexurl = ?,
                token = ?,
                filmslibrary = ?,
                library3d = ?,
                t1 = ?,
                t2 = ?,
                t3 = ?,
                t4 = ?,
                t5 = ?,
                backup = ?,
                posters4k = ?,
                mini4k = ?,
                hdr = ?,
                posters3d = ?,
                mini3d = ?,
                disney = ?,
                pixar = ?,
                hide4k = ?,
                transcode = ?
            WHERE id = ?
          """
        try:
            
            c = conn.cursor()
            c.execute(sql_update, old_config)
            conn.commit()
        except Exception as e:
            logger.error(e)
        finally:
            logger.info('Config migration successful')

    old_config = (baseurl, token, plexlibrary, library3d, t1, t2, t3, t4, t5, backup, posters4k, mini4k, hdr, posters3d, mini3d, disney, pixar, hide4k, transcode, 1)
    update_config(conn, old_config)

    conn.close()

def fresh_hdr_posters():
    conn = sqlite3.connect('app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    tmdb.api_key = config[0][25]

    logger.info("Restore-posters: Restore backup posters starting now") 
    for i in films.search(hdr='true'):  
        if config[0][26] == 0:
            # Try to restore from local posters first. If they don't exist, restore from TMDB
            newdir = os.path.dirname(re.sub(config[0][5], '/mnt/plex', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png') 
            if backup == True:
                poster = newdir+'poster_bak.png'
                logger.info(i.title+ ' Restored')
                i.uploadPoster(filepath=poster)
                os.remove(poster)
            else:
                tmdb_search = search.movies({"query": i.title, "year": i.year})
                logger.info(i.title)
                def get_poster_link():
                    for r in tmdb_search:
                        poster = r.poster_path
                        return poster
                def get_poster(poster):
                    r = requests.get(poster_url_base+poster, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open('tmdb_poster_restore.png', 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                            i.uploadPoster(filepath='tmdb_poster_restore.png')
                            os.remove('tmdb_poster_restore.png')
                try:
                    poster = get_poster_link()  
                    get_poster(poster) 
                except TypeError:
                    logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                    continue
        elif config[0][26] == 1:
            tmdb_search = search.movies({"query": i.title, "year": i.year})
            logger.info(i.title)
            def get_poster_link():
                for r in tmdb_search:
                    poster = r.poster_path
                    return poster
            def get_poster(poster):
                r = requests.get(poster_url_base+poster, stream=True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open('tmdb_poster_restore.png', 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                        i.uploadPoster(filepath='tmdb_poster_restore.png')
                        os.remove('tmdb_poster_restore.png')
            try:
                poster = get_poster_link()  
                get_poster(poster) 
            except TypeError:
                logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                continue
    posters4k()

    

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


#var = sys.argv[1]
#var2 = sys.argv[2]
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
#films = plex.library.section(var2)
films = plex.library.section("Films")

def restore_hdr10():
    for i in films.search(hdr='true'):#title=var):
        t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
        resolution = i.media[0].videoResolution
        file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
        m = MediaInfo.parse(file, output='JSON')
        x = json.loads(m)
        hdr_version = ""
        print(i.title)
        #print(x['media']['track'][1])
        try:
            hdr_version = x['media']['track'][1]['HDR_Format_String']
        except KeyError:
            pass
        if "dolby" not in str.lower(hdr_version):
            try:
                hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
            except KeyError:
                pass
        audio = ""
        while True:
            for f in range(10):
                if 'Audio' in x['media']['track'][f]['@@type']:
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
        if hdr_version != "":
            print(i.title+" - "+hdr_version+" - "+audio)
        else:
            print(i.title+" - SDR - "+audio)


        def restore():
            def restore_tmdb():
                print("RESTORE: restoring posters from TheMovieDb")
                tmdb_search = search.movies({"query": i.title, "year": i.year})
                print(i.title)
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
                    print("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                    pass
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png') 
            print(newdir)
            if backup == True:
                print("RESTORE: restoring posters from Local Backups")
                poster = newdir+'poster_bak.png'

                print(i.title+ ' Restored')
                i.uploadPoster(filepath=poster)
            else:
                print('no backup')
        if "hdr10+" in str.lower(hdr_version):
            print(i.title+' restore')
            restore()

def posters4k():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])

    if config[0][13] == 1:
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

            logger.info("4k Posters: 4k HDR poster script starting now.")

            def atmos_poster():
                logger.info(i.title+' Atmos Poster')
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(a_box)
                hash0 = imagehash.average_hash(backgroundchk)
                hash1 = imagehash.average_hash(atmos_box)
                cutoff= 10
                if hash0 - hash1 < cutoff:
                    logger.info('4k Posters: Atmos banner exists, moving on')
                else:    
                    background.paste(atmos, (0, 0), atmos)
                    background.save(tmp_poster)    
            def dtsx_poster():
                logger.info(i.title+' DTS:X Poster')
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(a_box)
                hash0 = imagehash.average_hash(backgroundchk)
                hash1 = imagehash.average_hash(dtsx_box)
                cutoff= 10
                if hash0 - hash1 < cutoff:
                    logger.info('4k Posters: DTS:X banner exists, moving on')
                else:    
                    background.paste(dtsx, (0, 0), dtsx)
                    background.save(tmp_poster)
            def check_for_mini():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
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
                background = Image.open(tv_poster)
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
                background = Image.open(tv_poster)
                background = background.resize(tv_size,Image.ANTIALIAS)
                background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
                background.save(tv_poster)
                #i.uploadPoster(filepath='/tmp/poster.png')
            def check_for_banner():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(box)
                hash0 = imagehash.average_hash(backgroundchk)
                hash1 = imagehash.average_hash(chk_banner)
                cutoff= 5
                if hash0 - hash1 < cutoff:
                    logger.info('4k Posters: 4K banner exists, moving on')
                else:
                    check_for_mini()   
            def add_banner():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                background.paste(banner_4k, (0, 0), banner_4k)
                background.save(tmp_poster)
                #i.uploadPoster(filepath='/tmp/poster.png')
            def add_mini_banner():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
                background.save(tmp_poster)
                #i.uploadPoster(filepath='/tmp/poster.png')
            def add_new_hdr():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(hdr_box)
                hash0 = imagehash.average_hash(backgroundchk)
                hash1 = imagehash.average_hash(chk_new_hdr)
                hash2 = imagehash.average_hash(chk_dolby_vision)
                hash3 = imagehash.average_hash(chk_hdr10)
                cutoff= 10

                def recreate_poster():
                    os.remove(tmp_poster)
                    def restore_tmdb():
                        logger.info("RESTORE: restoring posters from TheMovieDb")
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
                                with open('/tmp/poster.png', 'wb') as f:
                                    shutil.copyfileobj(r.raw, f)
                        try:
                            poster = get_poster_link()
                            get_poster(poster) 
                        except TypeError:
                            logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                                                   
                        
                    newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                    backup = os.path.exists(newdir+'poster_bak.png') 
                    if backup == True:
                        poster = newdir+'poster_bak.png'
                        shutil.copy(poster, '/tmp/poster.png')
                    elif config[0][26] == 1 and backup == False:
                        restore_tmdb()
                def dolby_vision():
                    logger.info("HDR Banner: "+i.title+" adding dolby-vision hdr banner")
                    background = Image.open(tmp_poster)
                    try:
                        background = background.resize(size,Image.ANTIALIAS)
                    except OSError as e:
                        logger.error(e)
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        background = background.resize(size,Image.ANTIALIAS)
                        ImageFile.LOAD_TRUNCATED_IMAGES = False
                    background.paste(banner_dv, (0, 0), banner_dv)
                    background.save(tmp_poster)    
                def hdr10():
                    logger.info("HDR Banner: "+i.title+" adding HDR10+ banner")
                    background = Image.open(tmp_poster)
                    try:
                        background = background.resize(size,Image.ANTIALIAS)
                    except OSError as e:
                        logger.error(e)
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        background = background.resize(size,Image.ANTIALIAS)
                        ImageFile.LOAD_TRUNCATED_IMAGES = False
                    background.paste(banner_hdr10, (0, 0), banner_hdr10)
                    background.save(tmp_poster) 
                def hdr():
                    logger.info("HDR Banner: "+i.title+" adding hdr banner now")
                    background = Image.open(tmp_poster)
                    try:
                        background = background.resize(size,Image.ANTIALIAS)
                    except OSError as e:
                        logger.error(e)
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        background = background.resize(size,Image.ANTIALIAS)
                        ImageFile.LOAD_TRUNCATED_IMAGES = False
                    background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
                    background.save(tmp_poster)
                
                if "dolby" and "vision" in str.lower(hdr_version):
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists moving on")
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                        recreate_poster()
                        dolby_vision()
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists")
                        recreate_poster()
                        dolby_vision()
                    else:
                        dolby_vision()
                elif "hdr10+" in str.lower(hdr_version):
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        hdr10()
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                        recreate_poster()
                        hdr10()                        
                    else:
                        hdr10()
                else:
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        hdr()
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                        recreate_poster()
                        hdr()
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                    else:
                        hdr()         
            def add_hdr():
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(hdr_box)
                hash0 = imagehash.average_hash(backgroundchk)
                hash1 = imagehash.average_hash(chk_hdr)
                cutoff= 5
                if hash0 - hash1 < cutoff:
                    logger.info('HDR Banner: '+i.title+' HDR banner exists, moving on...')
                else:
                    background.paste(banner_hdr, (0, 0), banner_hdr)
                    background.save(tmp_poster)
                    #i.uploadPoster(filepath='/tmp/poster.png')            
            def check_for_old_banner(): 
                background = Image.open(tmp_poster)
                try:
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                    ImageFile.LOAD_TRUNCATED_IMAGES = False
                backgroundchk = background.crop(hdr_box)
                hash0 = imagehash.average_hash(backgroundchk)   
                hash4 = imagehash.average_hash(chk_hdr)
                cutoff= 5
                if hash0 - hash4 < cutoff:
                    logger.info(i.title+" has old hdr banner")
                    for a in i:
                        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
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
                                    with open('/tmp/poster.png', 'wb') as f:
                                        shutil.copyfileobj(r.raw, f)
                                        i.uploadPoster(filepath='/tmp/poster.png')
                                        logger.info(i.title+" Restored from TMDb")
                            try:
                                poster = get_poster_link()  
                                get_poster(poster) 
                            except TypeError:
                                logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                                continue                          
            def get_poster():
                newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                backup = os.path.exists(newdir+'poster_bak.png')
                imgurl = i.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = tmp_poster              
                try:
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
                                    logger.info(i.title+' - 4k Posters: Backup file exists, skipping')    
                                else:
                                    #Check to see if the poster has a 4k Banner
                                    background = Image.open(filename)
                                    try:
                                        background = background.resize(size,Image.ANTIALIAS)
                                    except OSError as e:
                                        logger.error(e)
                                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                                        background = background.resize(size,Image.ANTIALIAS)
                                        ImageFile.LOAD_TRUNCATED_IMAGES = False
                                    backgroundchk = background.crop(box)
                                    hash0 = imagehash.average_hash(backgroundchk)
                                    hash1 = imagehash.average_hash(chk_banner)
                                    cutoff= 5
                                    if hash0 - hash1 < cutoff:
                                        logger.info('4k Posters: Poster has 4k Banner, Skipping Backup')
                                    else:
                                        #Check if the poster has a mini 4k banner
                                        background = Image.open(filename)
                                        try:
                                            background = background.resize(size,Image.ANTIALIAS)
                                        except OSError as e:
                                            logger.error(e)
                                            ImageFile.LOAD_TRUNCATED_IMAGES = True
                                            background = background.resize(size,Image.ANTIALIAS)
                                            ImageFile.LOAD_TRUNCATED_IMAGES = False
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
                                            shutil.copyfile(filename, newdir+'poster_bak.png')
                            else:        
                                logger.info(i.title+' - Posters: Creating a backup file')
                                try:
                                    shutil.copyfile(filename, newdir+'poster_bak.png')
                                except IOError as e:
                                    logger.error(e)
                        
                    else:
                        logger.info("4k Posters: "+films.title+ 'cannot find the poster for this film')
                except OSError as e:
                    logger.error(e)
                    pass
            def get_TVposter():   
                newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
                backup = os.path.exists(newdir+'poster_bak.png')
                imgurl = i.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = tv_poster
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
                            try:
                                background = background.resize(size,Image.ANTIALIAS)
                            except OSError as e:
                                logger.error(e)
                                ImageFile.LOAD_TRUNCATED_IMAGES = True
                                background = background.resize(size,Image.ANTIALIAS)
                                ImageFile.LOAD_TRUNCATED_IMAGES = False
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
                                    shutil.copyfile(filename, newdir+'poster_bak.png')
                        else:        
                            logger.info('4k Posters: Creating a backup file')
                            shutil.copyfile(filename, newdir+'poster_bak.png')

                else:
                    logger.info("4k Posters: "+films.title+" cannot find the poster for this Episode")


            def poster_4k_hdr():
                logger.info(i.title + ' 4K HDR') 
                if config[0][28] == 1:
                    check_for_old_banner()
                    add_new_hdr()
                else:
                    add_hdr()          
                check_for_banner()  
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    os.remove(tmp_poster)                             

            def poster_4k():   
                logger.info(i.title + ' 4K Poster')
                check_for_banner()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    os.remove(tmp_poster)                             
            def poster_hdr():
                logger.info(i.title + ' HDR Poster')

                if config[0][28] == 1:
                    check_for_old_banner()
                    add_new_hdr()
                else:
                    add_hdr()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    os.remove(tmp_poster)                                             
            def posterTV_4k():   
                logger.info(i.title + " 4K Poster")
                get_TVposter()
                check_for_mini_tv()
                i.uploadPoster(filepath=tv_poster)                             
                os.remove(tv_poster) 
        else:
            logger.info('4K Posters script is not enabled in the config so will not run.')
        
        if config[0][24] == 1 and config[0][3] != 'None':
            for i in films.search():
                t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
                tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                resolution = i.media[0].videoResolution
                file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
                m = MediaInfo.parse(file, output='JSON')
                x = json.loads(m)
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
                hdr_version = str.lower(hdr_version)
                if config[0][35] == 1:
                    get_poster()
                    if 'Dolby' and 'Atmos' in audio:
                        audio = 'Dolby Atmos'
                    if audio == 'Dolby Atmos':
                        atmos_poster()
                    elif audio == 'DTS:X':
                        dtsx_poster()
                    if config[0][15] == 1:
                        if hdr_version != "" and resolution == '4k':
                            poster_4k_hdr()
                        elif hdr_version == "" and resolution == "4k":
                            poster_4k()
                        elif hdr_version != "" and resolution !="4k":
                            poster_hdr()                   
                    else:
                        logger.info('4k Posters: Creating 4K posters only')
                        if hdr_version == "" and resolution == "4k":
                            poster_4k()
                    if os.path.exists(tmp_poster) == True:
                        i.uploadPoster(filepath=tmp_poster)                    
                        try:
                            os.remove(tmp_poster)
                        except FileNotFoundError:
                            pass
                else:
                    get_poster()
                    if config[0][15] == 1:
                        if hdr_version != "" and resolution == '4k':
                            poster_4k_hdr()
                        elif hdr_version == "" and resolution == "4k":
                            poster_4k()
                        elif hdr_version != "" and resolution !="4k":
                            poster_hdr()                   
                    else:
                        logger.info('4k Posters: Creating 4K posters only')
                        if hdr_version == "" and resolution == "4k":
                            poster_4k()
                    if os.path.exists(tmp_poster) == True:
                        i.uploadPoster(filepath=tmp_poster)
                        try:
                            os.remove(tmp_poster)
                        except FileNotFoundError:
                            pass
        if config[0][23] == 1 and config[0][22] != 'None':
            tv = plex.library.section(config[0][22])
            for i in tv.searchEpisodes(resolution="4k"):
                try:
                    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
                    tv_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                    posterTV_4k()
                except FileNotFoundError as e:
                    logger.error(e)
                    logger.info("4k Posters: "+tv.title+" The 4k poster for this episode could not be created")
                    logger.info("This is likely because poster backups are enabled and the script can't find or doesn't have access to your backup location")             
        logger.info('4K/HDR Posters script has finished')

    else:
        logger.info("4K/HDR Posters is disabled in the config so it will not run.")
    c.close()
#restore_hdr10()
for i in films.search():
    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
    tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
    resolution = i.media[0].videoResolution
    file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
    m = MediaInfo.parse(file, output='JSON')
    x = json.loads(m)
    hdr_version = ""
    #try:
    #    hdr_version = x['media']['track'][1]['HDR_Format_String']
    #except (KeyError, IndexError):
    #    pass
    #if "dolby" not in str.lower(hdr_version):
    #    try:
    #        hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
    #    except (KeyError, IndexError):
    #        try:
    #            hdr_version = x['media']['track'][1]['HDR_Format_Commercial_IfAny']
    #        except (KeyError, IndexError):
    #            pass
    audio = ""
    while True:
        try:
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
    
    print(audio)
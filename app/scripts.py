
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
tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
search = Search()
movie = Movie()
discover = Discover()


def recently_added_posters(webhooktitle):
    
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
                elif config[0][14] == 1:
                    add_mini_banner()
                else:
                    add_banner()  
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
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass  
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
                            gv = [v for v in g 
                                            if v.isnumeric()]
                            g = "".join(gv)
                            return g
                        g = get_tmdb_guid()
                        tmdb_search = movie.details(movie_id=g)
                        logger.info(i.title)
                        def get_poster(poster):
                            r = requests.get(poster_url_base+poster, stream=True)
                            if r.status_code == 200:
                                r.raw.decode_content = True
                                with open('/tmp/poster.png', 'wb') as f:
                                    shutil.copyfileobj(r.raw, f)
                        try:
                            poster = tmdb_search.poster_path
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
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists")
                        recreate_poster()
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                    else:
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                elif "hdr10+" in str.lower(hdr_version):
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                        recreate_poster()
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)                      
                    else:
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)
                else:
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                        recreate_poster()
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                    else:
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)        
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
                                    return r.poster_path
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
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass                             

            def poster_4k():   
                logger.info(i.title + ' 4K Poster')
                check_for_banner()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass

            def poster_hdr():
                logger.info(i.title + ' HDR Poster')

                if config[0][28] == 1:
                    check_for_old_banner()
                    add_new_hdr()
                else:
                    add_hdr()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass                                             
        else:
            logger.info('4K Posters script is not enabled in the config so will not run.')
        
        if config[0][24] == 1 and config[0][3] != 'None':
            if config[0][15] or config[0][35] == 1:
                for i in films.search(title=webhooktitle):
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
                        logger.error(e)
                        pass
                    hdr_version = str.lower(hdr_version)
                    if config[0][35] == 1:
                        try:
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
                        except Exception as e:
                            logger.error(e)
                    else:
                        try:
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
                        except Exception as e:
                            logger.error(e)                        
                    if os.path.exists(tmp_poster) == True:
                        i.uploadPoster(filepath=tmp_poster)
                        try:
                            os.remove(tmp_poster)
                        except FileNotFoundError:
                            pass
            else:
                try:
                    for i in films.search(title=webhooktitle, resolution='4k'):
                        t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
                        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')                
                        get_poster()
                        poster_4k()
                        if os.path.exists(tmp_poster) == True:
                            i.uploadPoster(filepath=tmp_poster)
                            try:
                                os.remove(tmp_poster)
                            except FileNotFoundError:
                                pass                
                except Exception as e:
                    logger.error(e) 
        logger.info('Script Finished')
    else:
        logger.info("4K/HDR Posters is disabled in the config so it will not run.")
    c.close()

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
                elif config[0][14] == 1:
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
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass  
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
                            gv = [v for v in g 
                                            if v.isnumeric()]
                            g = "".join(gv)
                            return g
                        g = get_tmdb_guid()
                        tmdb_search = movie.details(movie_id=g)
                        logger.info(i.title)
                        def get_poster(poster):
                            r = requests.get(poster_url_base+poster, stream=True)
                            if r.status_code == 200:
                                r.raw.decode_content = True
                                with open('/tmp/poster.png', 'wb') as f:
                                    shutil.copyfileobj(r.raw, f)
                        try:
                            poster = tmdb_search.poster_path
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
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists")
                        recreate_poster()
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                    else:
                        try:
                            dolby_vision()
                        except FileNotFoundError as e:
                            logger.error(e)
                elif "hdr10+" in str.lower(hdr_version):
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                        recreate_poster()
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)                      
                    else:
                        try:
                            hdr10()
                        except FileNotFoundError as e:
                            logger.error(e)
                else:
                    if hash0 - hash2 < cutoff:
                        logger.info("HDR Banner: "+i.title+" dolby-vision banner exists")
                        recreate_poster()
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash3 < cutoff:
                        logger.info("HDR Banner: "+i.title+" HDR10+ banner exists")
                        recreate_poster()
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)
                    elif hash0 - hash1 < cutoff:
                        logger.info("HDR Banner: "+i.title+" hdr banner exists moving on")
                    else:
                        try:
                            hdr()
                        except FileNotFoundError as e:
                            logger.error(e)        
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
                                    return r.poster_path
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
                                        logger.info('4k Posters: Poster has Mini 4k Banner,     Skipping Backup')
                                    else:
                                        logger.info('4k Posters: New poster detected, creating  new Backup') 
                                        os.remove(poster)
                                        logger.info('4k Posters: Check passed, creating a backup    file')
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
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass                             

            def poster_4k():   
                logger.info(i.title + ' 4K Poster')
                check_for_banner()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass

            def poster_hdr():
                logger.info(i.title + ' HDR Poster')

                if config[0][28] == 1:
                    check_for_old_banner()
                    add_new_hdr()
                else:
                    add_hdr()
                if os.path.exists(tmp_poster) == True:
                    i.uploadPoster(filepath=tmp_poster)                    
                    try:
                        os.remove(tmp_poster)
                    except FileNotFoundError:
                        pass                                             
            def posterTV_4k():   
                logger.info(i.title + " 4K Poster")
                get_TVposter()
                check_for_mini_tv()
                i.uploadPoster(filepath=tv_poster)                             
                os.remove(tv_poster) 
        else:
            logger.info('4K Posters script is not enabled in the config so will not run.')
        
        if config[0][24] == 1 and config[0][3] != 'None':
            if config[0][15] or config[0][35] == 1:
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
                        logger.error(e)
                        pass
                    hdr_version = str.lower(hdr_version)
                    if config[0][35] == 1:
                        try:
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
                        except Exception as e:
                            logger.error(e)
                    else:
                        try:
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
                        except Exception as e:
                            logger.error(e)                        
                    if os.path.exists(tmp_poster) == True:
                        i.uploadPoster(filepath=tmp_poster)
                        try:
                            os.remove(tmp_poster)
                        except FileNotFoundError:
                            pass
            else:
                try:
                    for i in films.search(resolution='4k'):
                        t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
                        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')                
                        get_poster()
                        poster_4k()
                        if os.path.exists(tmp_poster) == True:
                            i.uploadPoster(filepath=tmp_poster)
                            try:
                                os.remove(tmp_poster)
                            except FileNotFoundError:
                                pass                
                except Exception as e:
                    logger.error(e)                                
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

def tv4kposter():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    mini_4k_banner = Image.open("app/img/4K-mini-Template.png")
    chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
    size = (911,1367)
    tv_size = (1280,720)
    mini_box = (0,0,150,125)   

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
            logger.info("4k Posters: "+i.title+" cannot find the poster for this Episode")

    def posterTV_4k():   
        logger.info(i.title + " 4K Poster")
        get_TVposter()
        check_for_mini_tv()
        i.uploadPoster(filepath=tv_poster)  
        os.remove(tv_poster) 

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

def posters3d(): 
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    if config[0][16] == 1:


        banner_3d = Image.open("app/img/3D-Template.png")
        mini_3d_banner = Image.open("app/img/3D-mini-Template.png")

        chk_banner = Image.open("app/img/chk_3d_wide.png")
        chk_mini_banner = Image.open("app/img/chk-3D-mini.png")

        size = (911,1367)
        box= (0,0,911,100)
        mini_box = (0,0,301,268)

        logger.info("3D Posters: 3D poster script starting now.")  

        def check_for_mini():
            background = Image.open('/tmp/poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            backgroundchk = background.crop(mini_box)
            hash0 = imagehash.average_hash(backgroundchk)
            hash1 = imagehash.average_hash(chk_mini_banner)
            cutoff= 15
            if hash0 - hash1 < cutoff:
                logger.info('3D Posters: Mini 3D banner exists, moving on...')
            elif config[0][17] == 1:
                add_mini_banner()
            else:
                add_banner()       

        def check_for_banner():
            background = Image.open('/tmp/poster.png')
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
            background = Image.open('/tmp/poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            background.paste(banner_3d, (0, 0), banner_3d)
            background.save('/tmp/poster.png')
            i.uploadPoster(filepath='/tmp/poster.png')

        def add_mini_banner():
            background = Image.open('/tmp/poster.png')
            background = background.resize(size,Image.ANTIALIAS)
            background.paste(mini_3d_banner, (0, 0), mini_3d_banner)
            background.save('/tmp/poster.png')
            i.uploadPoster(filepath='/tmp/poster.png')        

        def get_poster():
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')
            imgurl = i.posterUrl
            img = requests.get(imgurl, stream=True)
            if img.status_code == 200:
                img.raw.decode_content = True
                filename = "/tmp/poster.png"

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
                            shutil.copyfile(filename, newdir+' poster_bak.png')
                    else:        
                        logger.info('3D Posters: Creating a backup file')
                        shutil.copyfile(filename, newdir+' poster_bak.png')
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
    else:
        logger.warning('3D Posters script is not enabled in the config so will not run')
    c.close()

def restore_posters():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])

        
    def continue_restore():
        logger.info("Restore-posters: Restore backup posters starting now")
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
                gv = [v for v in g 
                                if v.isnumeric()]
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
        def restore():
                logger.info("RESTORE: restoring posters from Local Backups")
                poster = newdir+'poster_bak.png'
                logger.info(i.title+ ' Restored')
                i.uploadPoster(filepath=poster)


        for i in films.search():
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')
            if backup == True:
                try:
                    restore()
                except OSError as e:
                    if e.errno == 2:
                        logger.debug(e)
            elif config[0][26] == 1 and backup == False:
                file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)          
                m = MediaInfo.parse(file, output='JSON')
                x = json.loads(m)
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
                    logger.error(e)
                    pass
                try:
                    hdr_version = str.lower(x['media']['track'][1]['HDR_Format_Commercial'])
                except KeyError:
                    try:
                        hdr_version = str.lower(x['media']['track'][1]['Format_Commercial_IfAny'])
                    except KeyError:
                        try:
                            hdr_version = str.lower(x['media']['track'][1]['HDR_Format'])
                        except KeyError:
                            hdr_version = 'Unknown'
                    
                if 'Dolby' and 'Atmos' in audio:
                    audio = 'Dolby Atmos'
                if audio == 'Dolby Atmos':
                    restore_tmdb()
                elif audio == 'DTS:X':
                    restore_tmdb()
                elif i.media[0].videoResolution == '4k':
                    restore_tmdb()
                elif hdr_version != 'unknown':
                    restore_tmdb()


    def check_connection():
        try:
            plex = PlexServer(config[0][1], config[0][2])
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            logger.error('Cannot connect to your plex server. Please double check your config is correct.')
        else:
            continue_restore()                
    check_connection()
    c.close()
    for i in films.search():
        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        backup = os.path.join(newdir+'poster_bak.png')            
        try:
            os.remove(backup)
        except PermissionError as e:
            logger.error(e)
        except FileNotFoundError as e:
            logger.error(e)
    logger.info('Restore Completed.')

def hide4k():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    if config[0][20] == 1:


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
    else:
        logger.warning('Hide 4K films is not enabled in the config so will not run')
    c.close()

def migrate():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    from configparser import ConfigParser
    config_object = ConfigParser()
    config_object.read("/config/config.ini")
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
    
    conn = sqlite3.connect('/config/app.db')
    
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
    c.close()

def fresh_hdr_posters():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    def continue_fresh_posters():
        logger.info("Restore-posters: Restore backup posters starting now") 
        for i in films.search(hdr='true'):  
            def restore_tmdb():
                g = str(i.guids[1])
                g = re.sub(">", "", g.split("//")[1])
                tmdb_search = movie.details(movie_id=g)
                tmdb_search = search.movies({"query": i.title, "year": i.year})
                logger.info(i.title)
                def get_poster(poster):
                    r = requests.get(poster_url_base+poster, stream=True)
                    if r.status_code == 200:
                        r.raw.decode_content = True
                        with open('tmdb_poster_restore.png', 'wb') as f:
                            shutil.copyfileobj(r.raw, f)
                            i.uploadPoster(filepath='tmdb_poster_restore.png')
                            os.remove('tmdb_poster_restore.png')
                            logger.info(i.title+' Restored from TheMovieDb')
                try:
                    poster = tmdb_search.poster_path
                    get_poster(poster) 
                except TypeError:
                    logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                    pass                        
            
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png') 
            if backup == True:
                poster = newdir+'poster_bak.png'
                logger.info(i.title+ ' Restored from Local files')
                i.uploadPoster(filepath=poster)
                os.remove(poster)
            elif config[0][26] == 1 and backup == False:
                restore_tmdb()
        posters4k()
    def check_connection():
        try:
            plex = PlexServer(config[0][1], config[0][2])
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            logger.error('Cannot connect to your plex server. Please double check your config is correct.')
        else:
            continue_fresh_posters()
    check_connection()
    c.close()

def autocollections():
    logger.info('Autocollections has started')
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])
    added = films.search(sort='titleSort')
    def popular():
        p_collection = []
        for i in range(3):
            i += 1
            popular = discover.discover_movies({
                "page": i,
                "with_original_language": "en"
            })
            for p in popular:
                for p in popular:
                    title= p.title
                    y = p.release_date.split("-")
                    p_collection.append((p.title, y[0]))
                    in_library = films.search(title=title, year=y[0])
                    for i in in_library:
                        if len(in_library) != 0:
                            i.addCollection('Popular')
        m_collection = [(m.title, m.year) for m in films.search(collection='Popular')]
        not_in_collection = list(set(m_collection) - set(p_collection))
        for m in films.search(collection='Popular'):
            if m.title in not_in_collection:
                m.removeCollection('Popular')
        logger.info("Popular Collection has finished")        
    def top_rated():
        tr_collection = []
        for i in range(3):
            i += 1
            top_rated = movie.top_rated({
                "page": i,
            })

            for x in top_rated:
                title= x.title
                y = x.release_date.split("-")
                tr_collection.append(x.title)
                in_library = films.search(title=title, year=y[0])
                for i in in_library:
                    if len(in_library) != 0:
                        i.addCollection('Top Rated')
        trm_collection = [m.title for m in films.search(collection='Top Rated')]
        not_in_collection = list(set(trm_collection) - set(tr_collection))
        for m in films.search(collection='Top Rated'):
            if m.title in not_in_collection:
                m.removeCollection('Top Rated')
        logger.info("Top Rated Collection has finished")
    def recommended():
        if config[0][33] != '':
            try:
                tautulli_api = RawAPI(base_url=config[0][32], api_key=config[0][33])
                i=tautulli_api.get_home_stats(stats_type='plays', stat_id='top_movies')
                x = json.dumps(tautulli_api.get_home_stats(stats_type='plays', stat_id='top_movies'))
                i=json.loads(x)
                top_watched=i["rows"][0]["title"]
                tw_year=i["rows"][0]["year"]
                a = search.movies({ "query": top_watched, "year": tw_year })
                for b in a:
                    i = b.id
                rec = movie.recommendations(movie_id=i)
                for r in rec:
                    title = r.title
                    y = r.release_date.split("-")
                    in_library = films.search(title=title, year=y[0])
                    for i in in_library:
                        if len(in_library) != 0:
                            i.addCollection('Recommended')
                rm_collection = [m.title for m in films.search(collection='Recommended')]
                r_collection = [r.title for r in rec]
                not_in_collection = list(set(rm_collection) - set(r_collection))
                for m in films.search(collection='Recommended'):
                    if m.title in not_in_collection:
                        m.removeCollection('Recommended')
            except requests.exceptions.ConnectionError as e:
                pass
        logger.info("Reccomended Collection has finished")
    def MCU():
        try:
            collection = 'Marvel Cinematic Universe'
            c = films.collection(title=collection)
            if c.smart == False:
                imgurl = c.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = "/tmp/poster.png"
                if img.status_code == 200:
                    img.raw.decode_content = True
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(img.raw, f)
                c.delete()
                plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': 'Marvel Studios'})
                d = films.collection(collection)
                d.uploadPoster(filepath='/tmp/poster.png')
            if config[0][31] == 1:
                c.uploadPoster(filepath='app/img/collections/mcu_poster.png')
        except plexapi.exceptions.NotFound:
            plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': 'Marvel Studios'})
            d = films.collection(collection)
            if config[0][31] == 1:
                        d.uploadPoster(filepath='app/img/collections/mcu_poster.png') 

    def pixar():
        try:
            collection = 'Pixar'
            c = films.collection(title=collection)
            if c.smart == False:
                imgurl = c.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = "/tmp/poster.png"
                if img.status_code == 200:
                    img.raw.decode_content = True
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(img.raw, f)
                c.delete()
                plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': collection})
                d = films.collection(collection)
                d.uploadPoster(filepath='/tmp/poster.png')
            if config[0][31] == 1:
                c.uploadPoster(filepath='app/img/collections/pixar_poster.jpeg')                    
        except plexapi.exceptions.NotFound:
            plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': collection})
            d = films.collection(collection)
            if config[0][31] == 1:
                        d.uploadPoster(filepath='app/img/collections/pixar_poster.jpeg')

    def disney():
        try:
            collection = 'Disney'
            c = films.collection(title=collection)
            if c.smart == False:
                imgurl = c.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = "/tmp/poster.png"
                if img.status_code == 200:
                    img.raw.decode_content = True
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(img.raw, f)
                c.delete()
                plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': collection})
                d = films.collection(collection)
                d.uploadPoster(filepath='/tmp/poster.png')
            if config[0][31] == 1:
                c.uploadPoster(filepath='app/img/collections/disney_poster.jpeg') 
        except plexapi.exceptions.NotFound:
            plex.createCollection(section=config[0][3], title=collection, smart=True, filters={'studio': collection})
            d = films.collection(collection)
            if config[0][31] == 1:
                        d.uploadPoster(filepath='app/img/collections/disney_poster.jpeg')

    if config[0][18] == 1:
        disney()

    if config[0][19] == 1:
        pixar()
    if config[0][34] == 1:
        MCU()                
    if config[0][29] == 1:
        popular()
        top_rated()
        recommended() 
    logger.info("Auto Collections has finished")
    c.close()

def remove_unused_backup_files():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])

    chk_banner = Image.open("app/img/chk-4k.png")
    chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
    chk_hdr = Image.open("app/img/chk_hdr.png")
    chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
    chk_hdr10 = Image.open("app/img/chk_hdr10.png")
    chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
    banner_new_hdr = Image.open("app/img/hdr.png")
    atmos_box = Image.open("app/img/chk_atmos.png")
    dtsx_box = Image.open("app/img/chk_dtsx.png") 
    size = (911,1367)
    tv_size = (1280,720)
    box= (0,0,911,100)
    mini_box = (0,0,150,125)
    hdr_box = (0,605,225,731)
    a_box = (0,731,225,803)
    
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    def hdr_check():
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
        if (
            hash0 - hash2 >= cutoff
            and hash0 - hash1 >= cutoff
            and hash0 - hash3 >= cutoff
        ):
            logger.info(i.title+' No banners found')
            try:
                os.remove(b_poster)
            except FileNotFoundError:
                pass
    def dts_check():
        background = Image.open(tmp_poster)
        backgroundchk = background.crop(a_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(dtsx_box)
        cutoff= 10
        if hash0 - hash1 >= cutoff:
            hdr_check
    def atmos_check():
        background = Image.open(tmp_poster)
        backgroundchk = background.crop(a_box)
        hash0 = imagehash.average_hash(backgroundchk)
        hash1 = imagehash.average_hash(atmos_box)
        cutoff= 10
        if hash0 - hash1 >= cutoff:
            dts_check()       
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
        if hash0 - hash1 >= cutoff:
            atmos_check()
            
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
        if hash0 - hash1 >= cutoff:
            check_for_mini()  
    def get_poster():
        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        imgurl = i.posterUrl
        img = requests.get(imgurl, stream=True)
        filename = tmp_poster              

        if img.status_code == 200:
            img.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img.raw, f)
    logger.info('Searching for un-used backup files, this may take a while')                
    for i in films.search():
        t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
        p = 'poster_bak.png'
        tmp_poster = re.sub(' ','_', '/tmp/poster.png')
        newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        b_poster = newdir+p
        if backup == True:
            #print(b_poster)
            get_poster()
            check_for_banner()
        
    try:
        os.remove(tmp_poster)
    except FileNotFoundError:
        pass  
    logger.info('Search complete')    
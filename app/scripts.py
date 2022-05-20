from PIL import Image, ImageFile
from plexapi.server import PlexServer
import plexapi
import requests
import shutil
import os
import re
import imagehash
import logging
from logging.handlers import RotatingFileHandler
from tmdbv3api import TMDb, Search, Movie, Discover
from pymediainfo import MediaInfo
import json
from tautulli import RawAPI
import unicodedata
from flask_sqlalchemy import sqlalchemy
import signal
import time

import random
import string

def setup_logger(logger_name, log_file):
    import sqlite3
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
discover = Discover()

b_dir = '/config/backup/' 

def recently_added_posters(webhooktitle):
    from app.models import Plex, film_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    global b_dir

    def run_script(): 
        banner_4k = Image.open("app/img/4K-Template.png")
        mini_4k_banner = Image.open("app/img/4K-mini-Template.png")
        banner_dv = Image.open("app/img/dolby_vision.png")
        banner_hdr10 = Image.open("app/img/hdr10.png")

        banner_new_hdr = Image.open("app/img/hdr.png")
        atmos = Image.open("app/img/atmos.png")
        dtsx = Image.open("app/img/dtsx.png")

        size = (911,1367)
        bannerbox= (0,0,911,100)
        mini_box = (0,0,150,125)
        hdr_box = (0,605,225,731)
        a_box = (0,731,225,803)

        cutoff = 10        
        def hdrp(tmp_poster):
            logger.info(i.title+" HDR Banner")
            background = Image.open(tmp_poster)
            background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
            background.save(tmp_poster)
        def dolby_vision(tmp_poster):
            logger.info(i.title+" Dolby Vision Banner")
            background = Image.open(tmp_poster)
            background.paste(banner_dv, (0, 0), banner_dv)
            background.save(tmp_poster)
        def hdr10(tmp_poster):
            logger.info(i.title+" HDR10+ banner")
            background = Image.open(tmp_poster)
            background.paste(banner_hdr10, (0, 0), banner_hdr10)
            background.save(tmp_poster)
        def atmos_poster(tmp_poster):
            logger.info(i.title+' Atmos Banner')
            background = Image.open(tmp_poster)
            background.paste(atmos, (0, 0), atmos)
            background.save(tmp_poster)   
        def dtsx_poster(tmp_poster):
            logger.info(i.title+' Atmos Banner')
            background = Image.open(tmp_poster)
            background.paste(dtsx, (0, 0), dtsx)
            background.save(tmp_poster)  
        def add_banner(tmp_poster):
            background = Image.open(tmp_poster)
            if config[0].mini4k == 1:
                logger.info(i.title+' Adding Mini 4K Banner')
                background.paste(mini_4k_banner, (0,0), mini_4k_banner)
            else:
                logger.info(i.title+' Adding 4k Banner')
                background.paste(banner_4k, (0, 0), banner_4k)
            background.save(tmp_poster)           
        def scan_files():
            logger.debug('Scanning '+i.title)
            if config[0].plexpath == '/':
                file = '/films'+i.media[0].parts[0].file
            else:
                file = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
            m = MediaInfo.parse(file, output='JSON')
            x = json.loads(m)
            hdr_version = get_plex_hdr()
            try:
                hdr_version = x['media']['track'][1]['HDR_Format_String']
            except (KeyError, IndexError):
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
                                if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                                    audio = 'DTS:X'
                                break
                            elif 'Format' in x['media']['track'][f]:
                                audio = x['media']['track'][f]['Format']
                                break
                    if audio != "":
                        break
            except (IndexError, KeyError) as e:
                logger.debug(i.title+' '+repr(e))
            return audio, hdr_version

        def upload_poster(tmp_poster):
            if os.path.exists(tmp_poster) == True:
                i.uploadPoster(filepath=tmp_poster)                    
                try:
                    os.remove(tmp_poster)
                except FileNotFoundError:
                    pass             

        def insert_intoTable(hdr, audio, tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')            
            logger.debug('Adding '+i.title+' to database') 
            logger.debug(i.title+' '+hdr+' '+audio)  
            b_file = backup_poster(tmp_poster)
            b_file = re.sub('/config', 'static', b_file)
            if backup == True or True not in banners:
                film = film_table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file, checked='1')
                db.session.add(film)
                db.session.commit()

        def updateTable(hdr, audio, tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(r[0].poster)
            logger.debug('Updating '+i.title+' in database')
            logger.debug(i.title+' '+hdr+' '+audio)   
            b_file = backup_poster(tmp_poster)
            b_file = re.sub('/config', 'static', b_file)
            if backup == True or True not in banners:
                row = r[0].id
                film = film_table.query.get(row)
                film.size = size
                film.res = res
                film.hdr = hdr
                film.audio = audio
                film.poster = b_file
                film.checked = '1'
                db.session.commit()

        def backup_poster(tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            old_backup = os.path.exists(newdir+'poster_bak.png')
            fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))

            if old_backup == True:
                bak_file = newdir+'poster_bak.png'
                b_file = b_dir+'films/'+fname+'.png'
                shutil.copy(bak_file, b_file)
                return b_file
            elif True not in banners:
                logger.debug(i.title+" No banners detected so adding backup file to database")
                try:
                    if r[0].poster:
                        b_file = re.sub('static', '/config', r[0].poster)
                    else:
                        b_file = b_dir+'films/'+fname+'.png'
                except:
                    b_file = b_dir+'films/'+fname+'.png'
                shutil.copy(tmp_poster, b_file)
                return b_file

        def check_banners(tmp_poster):
            size = (911,1367)
            try:
                background = Image.open(tmp_poster)
                background = background.resize(size,Image.LANCZOS)
            except OSError as e:
                logger.error(e)
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                background = background.resize(size,Image.LANCZOS)
                ImageFile.LOAD_TRUNCATED_IMAGES = False

            # Wide banner box
            bannerchk = background.crop(bannerbox)
            # Mini Banner Box
            minichk = background.crop(mini_box)
            # Audio Box
            audiochk = background.crop(a_box)
            # HDR Box
            hdrchk = background.crop(hdr_box)

            # POSTER HASHES
            # Wide Banner
            poster_banner_hash = imagehash.average_hash(bannerchk)
            # Mini Banner
            poster_mini_hash = imagehash.average_hash(minichk)
            # Audio Banner
            poster_audio_hash = imagehash.average_hash(audiochk)
            # HDR Banner
            poster_hdr_hash = imagehash.average_hash(hdrchk)

            # General Hashes
            chk_banner = Image.open("app/img/chk-4k.png")
            chk_banner_hash = imagehash.average_hash(chk_banner)

            chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
            chk_mini_banner_hash = imagehash.average_hash(chk_mini_banner)

            chk_hdr = Image.open("app/img/chk_hdr.png")
            chk_hdr_hash = imagehash.average_hash(chk_hdr)

            chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
            chk_dolby_vision_hash = imagehash.average_hash(chk_dolby_vision)

            chk_hdr10 = Image.open("app/img/chk_hdr10.png")
            chk_hdr10_hash = imagehash.average_hash(chk_hdr10)

            chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
            chk_new_hdr_hash = imagehash.average_hash(chk_new_hdr)

            atmos_box = Image.open("app/img/chk_atmos.png")
            chk_atmos_hash = imagehash.average_hash(atmos_box)

            dtsx_box = Image.open("app/img/chk_dtsx.png")
            chk_dtsx_hash = imagehash.average_hash(dtsx_box)

            wide_banner = mini_banner = audio_banner = hdr_banner = old_hdr = False

            if poster_banner_hash - chk_banner_hash < cutoff:
                wide_banner = True
            if poster_mini_hash - chk_mini_banner_hash < cutoff:
                mini_banner = True
            if (
                poster_audio_hash - chk_atmos_hash < cutoff
                or poster_audio_hash - chk_dtsx_hash < cutoff
            ):
                audio_banner = True
            if poster_hdr_hash - chk_hdr_hash < cutoff:
                old_hdr = True
            if (
                poster_hdr_hash - chk_new_hdr_hash < cutoff 
                or poster_hdr_hash - chk_dolby_vision_hash < cutoff 
                or poster_hdr_hash - chk_hdr10_hash < cutoff
            ):
                hdr_banner = True
            background.save(tmp_poster)
            return wide_banner, mini_banner, audio_banner, hdr_banner, old_hdr

        def get_plex_hdr():
            ekey = i.key
            m = plex.fetchItems(ekey)
            for m in m:
                try:
                    if m.media[0].parts[0].streams[0].DOVIPresent == True:
                        hdr_version='Dolby Vision'
                        i.addLabel('Dolby Vision', locked=False)
                    elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                        hdr_version='HDR'
                        i.addLabel('HDR', locked=False)
                    else:
                        hdr_version = 'None'
                    return hdr_version
                except IndexError:
                    pass

        def decision_tree(tmp_poster):
            
            wide_banner = banners[0]
            mini_banner = banners[1]
            audio_banner = banners[2]
            hdr_banner = banners[3]

            logger.debug(banners)

            # If there are no HDR banners and media info skip is enabled
            if (
                hdr_banner == False 
                and config[0].hdr == 1
                and config[0].skip_media_info == 1
                ):
                hdr_version = get_plex_hdr()
                if hdr_version == 'Dolby Vision':
                    dolby_vision(tmp_poster)
                elif hdr_version == 'HDR':
                    hdrp(tmp_poster)
            # If there are no HDR banners and either hdr or audio posters are enabled and skip media info is disabled
            elif config[0].skip_media_info == 0 and (
                hdr_banner == False 
                and config[0].hdr == 1
            ) or (
                audio_banner == False
                and config[0].audio_posters == 1
            ):     
                def database_decision(r):
                    try:
                        audio = r[0].audio
                        hdr = r[0].hdr
                        if str(r[0].guid) == guid:
                            logger.debug(title+' GUID Match')
                            if str(r[0].size) != (size):
                                logger.debug(title+" has changed, rescanning")
                                scan = scan_files()
                                audio = scan[0]
                                hdr = scan[1]
                                logger.debug(title+' - '+hdr)
                                if hdr == "":
                                    hdr = get_plex_hdr() 
                                    logger.debug(title+' - '+hdr)                               
                                updateTable(hdr, audio, tmp_poster)
                            else:
                                updateTable(hdr, audio, tmp_poster)
                                
                            if not r[0].poster and True not in banners:
                                updateTable(hdr, audio, tmp_poster)
                            else:
                                logger.debug(title+' is the same')
                        else:
                            scan = scan_files()
                            audio = scan[0]
                            hdr = scan[1]
                            logger.debug(hdr)
                            if hdr == "":
                                hdr = get_plex_hdr()
                            updateTable(hdr, audio, tmp_poster)
                    except Exception as e:
                        logger.error(repr(e))
                        scan = scan_files()
                        audio = scan[0]
                        hdr = scan[1]
                        try:
                            insert_intoTable(hdr, audio, tmp_poster)
                        except Exception as e: #sqlalchemy.exc.IntegrityError as e:
                            logger.warning(repr(e))
                            updateTable(hdr, audio, tmp_poster)
                    return audio, hdr

                def banner_decision():
                    if audio_banner == False:
                        if 'Atmos' in audio and config[0].audio_posters == 1:
                            atmos_poster(tmp_poster)
                        elif audio == 'DTS:X' and config[0].audio_posters == 1:
                            dtsx_poster(tmp_poster)
                    elif 'Atmos' in audio:
                        i.addLabel('Dolby Atmos', locked=False)
                    elif audio == 'DTS:X':
                        i.addLabel('DTS:X', locked=False)
                    if hdr_banner == False:
                        if 'Dolby Vision' in hdr and config[0].new_hdr == 1:
                            dolby_vision(tmp_poster)
                        elif "HDR10+" in hdr and config[0].new_hdr == 1:
                            hdr10(tmp_poster)
                        elif hdr == "None":
                            pass
                        elif (
                            hdr != ""
                            and config[0].new_hdr == 1
                        ):
                            hdrp(tmp_poster)
                    elif 'Dolby Vision' in hdr:
                        i.addLabel('Dolby Vision', locked=False)
                    elif 'HDR10+' in hdr:
                        i.addLabel('HDR10+', locked=False)
                    elif hdr != '':
                        i.addLabel('HDR', locked=False)                

                audio_hdr = database_decision(r)
                audio = audio_hdr[0]
                hdr = audio_hdr[1]
                banner_decision()

            if res == '4k' and config[0].films4kposters == 1:
                if wide_banner == mini_banner == False:
                    add_banner(tmp_poster)
                else:
                    logger.debug(i.title+' Has banner') 
            rechk_banners = check_banners(tmp_poster)
            if True not in rechk_banners:
                try:
                    os.remove(tmp_poster)
                except:
                    pass
        def check_for_new_poster(tmp_poster):
            if r:
                new_poster = 'False'
                try:
                    poster_file = r[0].poster
                    try:
                        bak_poster = Image.open(poster_file)
                        bak_poster_hash = imagehash.average_hash(bak_poster)
                        poster = Image.open(tmp_poster)
                        poster_hash = imagehash.average_hash(poster)
                    except SyntaxError as e:
                        logger.error(repr(e))
                    except OSError as e:
                        logger.error(e)
                        if 'FileNotFoundError'  or 'Errno 2 'in e:
                            logger.debug(i.title+' - Poster Not found')
                            shutil.copy(tmp_poster, poster_file)
                            new_poster = 'True'
                            return new_poster
                        else:
                            logger.debug(i.title)
                            logger.warning(repr(e))
                            ImageFile.LOAD_TRUNCATED_IMAGES = True
                            bak_poster = Image.open(poster_file)
                            bak_poster_hash = imagehash.average_hash(bak_poster)
                            poster = Image.open(tmp_poster)
                            poster_hash = imagehash.average_hash(poster)
                            ImageFile.LOAD_TRUNCATED_IMAGES = False

                         
                    if poster_hash - bak_poster_hash > cutoff:
                        logger.debug(i.title+' - Poster has changed')
                        shutil.copy(tmp_poster, poster_file)
                        new_poster = 'True'
                        return new_poster                      
                    else:
                        logger.debug('Poster has not changed')
                        return new_poster
                        
                    
                except:
                    pass

        def get_poster():
            logger.debug(i.title+' Getting poster')
            imgurl = i.posterUrl
            img = requests.get(imgurl, stream=True)
            filename = tmp_poster
            try:
                if img.status_code == 200:
                    img.raw.decode_content = True
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(img.raw, f)
                    return tmp_poster 
                else:
                    logger.info("4k Posters: "+films.title+ 'cannot find the poster for this film')
            except OSError as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)

        for i in films.search(title=webhooktitle):
            logger.info(i.title)           
            title = i.title
            guid = str(i.guid)
            guids = str(i.guids)
            size = i.media[0].parts[0].size
            res = i.media[0].videoResolution    
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
            tmp_poster = get_poster()     
            r = film_table.query.filter(film_table.guid == guid).all()
            try:
                if r[0].checked == 1:
                    logger.info(i.title+' has been checked, checking to see if file has changed')
                    if str(r[0].size) == str(size):
                        logger.info(title+' has been processed and the file has not changed, skiping')
                        new_poster = check_for_new_poster(tmp_poster)
                        print(new_poster)
                        if new_poster == 'True':
                            banners = check_banners(tmp_poster)
                            decision_tree(tmp_poster)
                            upload_poster(tmp_poster)
                    else:
                        logger.debug(i.title+' Checking for Banners')
                        banners = check_banners(tmp_poster)
                        decision_tree(tmp_poster)
                        upload_poster(tmp_poster)
                else:
                    logger.debug(i.title+' Checking for Banners')

                    check_for_new_poster(tmp_poster)                    
                    banners = check_banners(tmp_poster)
                    decision_tree(tmp_poster)
                    upload_poster(tmp_poster)
            except: 
                logger.debug('Poster retrieved')
                check_for_new_poster(tmp_poster)
                banners = check_banners(tmp_poster)
                decision_tree(tmp_poster)
                upload_poster(tmp_poster)
        dirpath = '/tmp/'
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.endswith('.png'):
                    os.remove(dirpath+file)       
        logger.info('4k Poster script has finished')
    lib = config[0].filmslibrary.split(',')
    logger.debug(lib)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass    

def posters4k():
    from app.models import Plex, film_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    global b_dir

    def run_script(): 
        banner_4k = Image.open("app/img/4K-Template.png")
        mini_4k_banner = Image.open("app/img/4K-mini-Template.png")
        banner_dv = Image.open("app/img/dolby_vision.png")
        banner_hdr10 = Image.open("app/img/hdr10.png")

        banner_new_hdr = Image.open("app/img/hdr.png")
        atmos = Image.open("app/img/atmos.png")
        dtsx = Image.open("app/img/dtsx.png")

        size = (911,1367)
        bannerbox= (0,0,911,100)
        mini_box = (0,0,150,125)
        hdr_box = (0,605,225,731)
        a_box = (0,731,225,803)

        cutoff = 10        
        def hdrp(tmp_poster):
            logger.info(i.title+" HDR Banner")
            background = Image.open(tmp_poster)
            background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
            background.save(tmp_poster)
        def dolby_vision(tmp_poster):
            logger.info(i.title+" Dolby Vision Banner")
            background = Image.open(tmp_poster)
            background.paste(banner_dv, (0, 0), banner_dv)
            background.save(tmp_poster)
        def hdr10(tmp_poster):
            logger.info(i.title+" HDR10+ banner")
            background = Image.open(tmp_poster)
            background.paste(banner_hdr10, (0, 0), banner_hdr10)
            background.save(tmp_poster)
        def atmos_poster(tmp_poster):
            logger.info(i.title+' Atmos Banner')
            background = Image.open(tmp_poster)
            background.paste(atmos, (0, 0), atmos)
            background.save(tmp_poster)   
        def dtsx_poster(tmp_poster):
            logger.info(i.title+' Atmos Banner')
            background = Image.open(tmp_poster)
            background.paste(dtsx, (0, 0), dtsx)
            background.save(tmp_poster)  
        def add_banner(tmp_poster):
            background = Image.open(tmp_poster)
            if config[0].mini4k == 1:
                logger.info(i.title+' Adding Mini 4K Banner')
                background.paste(mini_4k_banner, (0,0), mini_4k_banner)
            else:
                logger.info(i.title+' Adding 4k Banner')
                background.paste(banner_4k, (0, 0), banner_4k)
            background.save(tmp_poster)           
        def scan_files():
            logger.debug('Scanning '+i.title)
            if config[0].plexpath == '/':
                file = '/films'+i.media[0].parts[0].file
            else:
                file = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
            m = MediaInfo.parse(file, output='JSON')
            x = json.loads(m)
            hdr_version = get_plex_hdr()
            try:
                hdr_version = x['media']['track'][1]['HDR_Format_String']
            except (KeyError, IndexError):
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
                                if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                                    audio = 'DTS:X'
                                break
                            elif 'Format' in x['media']['track'][f]:
                                audio = x['media']['track'][f]['Format']
                                break
                    if audio != "":
                        break
            except (IndexError, KeyError) as e:
                logger.debug(i.title+' '+repr(e))
            return audio, hdr_version

        def upload_poster(tmp_poster):
            if os.path.exists(tmp_poster) == True:
                i.uploadPoster(filepath=tmp_poster)                    
                try:
                    os.remove(tmp_poster)
                except FileNotFoundError:
                    pass             

        def insert_intoTable(hdr, audio, tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')            
            logger.debug('Adding '+i.title+' to database') 
            logger.debug(i.title+' '+hdr+' '+audio)  
            b_file = backup_poster(tmp_poster)
            b_file = re.sub('/config', 'static', b_file)
            if backup == True or True not in banners:
                film = film_table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file, checked='1')
                db.session.add(film)
                db.session.commit()

        def updateTable(hdr, audio, tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(r[0].poster)
            logger.debug('Updating '+i.title+' in database')
            logger.debug(i.title+' '+hdr+' '+audio)   
            b_file = backup_poster(tmp_poster)
            b_file = re.sub('/config', 'static', b_file)
            if backup == True or True not in banners:
                row = r[0].id
                film = film_table.query.get(row)
                film.size = size
                film.res = res
                film.hdr = hdr
                film.audio = audio
                film.poster = b_file
                film.checked = '1'
                db.session.commit()

        def backup_poster(tmp_poster):
            if config[0].manualplexpath == 1:
                newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
            else:
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            old_backup = os.path.exists(newdir+'poster_bak.png')
            fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
            

            if old_backup == True:
                bak_file = newdir+'poster_bak.png'
                b_file = b_dir+'films/'+fname+'.png'
                shutil.copy(bak_file, b_file)
                return b_file
            elif True not in banners:
                logger.debug(i.title+" No banners detected so adding backup file to database")
                try:
                    if r[0].poster:
                        b_file = r[0].poster
                    else:
                        b_file = b_dir+'films/'+fname+'.png'
                except:
                    b_file = b_dir+'films/'+fname+'.png'
                shutil.copy(tmp_poster, b_file)
                return b_file

        def check_banners(tmp_poster):
            size = (911,1367)
            try:
                background = Image.open(tmp_poster)
                background = background.resize(size,Image.LANCZOS)
            except OSError as e:
                logger.error(e)
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                background = background.resize(size,Image.LANCZOS)
                ImageFile.LOAD_TRUNCATED_IMAGES = False

            # Wide banner box
            bannerchk = background.crop(bannerbox)
            # Mini Banner Box
            minichk = background.crop(mini_box)
            # Audio Box
            audiochk = background.crop(a_box)
            # HDR Box
            hdrchk = background.crop(hdr_box)

            # POSTER HASHES
            # Wide Banner
            poster_banner_hash = imagehash.average_hash(bannerchk)
            # Mini Banner
            poster_mini_hash = imagehash.average_hash(minichk)
            # Audio Banner
            poster_audio_hash = imagehash.average_hash(audiochk)
            # HDR Banner
            poster_hdr_hash = imagehash.average_hash(hdrchk)

            # General Hashes
            chk_banner = Image.open("app/img/chk-4k.png")
            chk_banner_hash = imagehash.average_hash(chk_banner)

            chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
            chk_mini_banner_hash = imagehash.average_hash(chk_mini_banner)

            chk_hdr = Image.open("app/img/chk_hdr.png")
            chk_hdr_hash = imagehash.average_hash(chk_hdr)

            chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
            chk_dolby_vision_hash = imagehash.average_hash(chk_dolby_vision)

            chk_hdr10 = Image.open("app/img/chk_hdr10.png")
            chk_hdr10_hash = imagehash.average_hash(chk_hdr10)

            chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
            chk_new_hdr_hash = imagehash.average_hash(chk_new_hdr)

            atmos_box = Image.open("app/img/chk_atmos.png")
            chk_atmos_hash = imagehash.average_hash(atmos_box)

            dtsx_box = Image.open("app/img/chk_dtsx.png")
            chk_dtsx_hash = imagehash.average_hash(dtsx_box)

            wide_banner = mini_banner = audio_banner = hdr_banner = old_hdr = False

            if poster_banner_hash - chk_banner_hash < cutoff:
                wide_banner = True
            if poster_mini_hash - chk_mini_banner_hash < cutoff:
                mini_banner = True
            if (
                poster_audio_hash - chk_atmos_hash < cutoff
                or poster_audio_hash - chk_dtsx_hash < cutoff
            ):
                audio_banner = True
            if poster_hdr_hash - chk_hdr_hash < cutoff:
                old_hdr = True
            if (
                poster_hdr_hash - chk_new_hdr_hash < cutoff 
                or poster_hdr_hash - chk_dolby_vision_hash < cutoff 
                or poster_hdr_hash - chk_hdr10_hash < cutoff
            ):
                hdr_banner = True
            background.save(tmp_poster)
            return wide_banner, mini_banner, audio_banner, hdr_banner, old_hdr

        def get_plex_hdr():
            ekey = i.key
            m = plex.fetchItems(ekey)
            for m in m:
                try:
                    if m.media[0].parts[0].streams[0].DOVIPresent == True:
                        hdr_version='Dolby Vision'
                        i.addLabel('Dolby Vision', locked=False)
                    elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                        hdr_version='HDR'
                        i.addLabel('HDR', locked=False)
                    else:
                        hdr_version = 'None'
                    return hdr_version
                except IndexError:
                    pass

        def decision_tree(tmp_poster):
            
            wide_banner = banners[0]
            mini_banner = banners[1]
            audio_banner = banners[2]
            hdr_banner = banners[3]

            logger.debug(banners)

            # If there are no HDR banners and media info skip is enabled
            if (
                hdr_banner == False 
                and config[0].hdr == 1
                and config[0].skip_media_info == 1
                ):
                hdr_version = get_plex_hdr()
                if hdr_version == 'Dolby Vision':
                    dolby_vision(tmp_poster)
                elif hdr_version == 'HDR':
                    hdrp(tmp_poster)
            # If there are no HDR banners and either hdr or audio posters are enabled and skip media info is disabled
            elif config[0].skip_media_info == 0 and (
                hdr_banner == False 
                and config[0].hdr == 1
            ) or (
                audio_banner == False
                and config[0].audio_posters == 1
            ):     
                def database_decision(r):
                    try:
                        audio = r[0].audio
                        hdr = r[0].hdr
                        if str(r[0].guid) == guid:
                            logger.debug(title+' GUID Match')
                            if str(r[0].size) != (size):
                                logger.debug(title+" has changed, rescanning")
                                scan = scan_files()
                                audio = scan[0]
                                hdr = scan[1]
                                logger.debug(title+' - '+hdr)
                                if hdr == "":
                                    hdr = get_plex_hdr() 
                                    logger.debug(title+' - '+hdr)                               
                                updateTable(hdr, audio, tmp_poster)
                            else:
                                updateTable(hdr, audio, tmp_poster)
                                
                            if not r[0].poster and True not in banners:
                                updateTable(hdr, audio, tmp_poster)
                            else:
                                logger.debug(title+' is the same')
                        else:
                            scan = scan_files()
                            audio = scan[0]
                            hdr = scan[1]
                            logger.debug(hdr)
                            if hdr == "":
                                hdr = get_plex_hdr()
                            updateTable(hdr, audio, tmp_poster)
                    except Exception as e:
                        logger.error(repr(e))
                        scan = scan_files()
                        audio = scan[0]
                        hdr = scan[1]
                        try:
                            insert_intoTable(hdr, audio, tmp_poster)
                        except Exception as e: #sqlalchemy.exc.IntegrityError as e:
                            logger.warning(repr(e))
                            updateTable(hdr, audio, tmp_poster)
                    return audio, hdr

                def banner_decision():
                    if audio_banner == False:
                        if 'Atmos' in audio and config[0].audio_posters == 1:
                            atmos_poster(tmp_poster)
                        elif audio == 'DTS:X' and config[0].audio_posters == 1:
                            dtsx_poster(tmp_poster)
                    elif 'Atmos' in audio:
                        i.addLabel('Dolby Atmos', locked=False)
                    elif audio == 'DTS:X':
                        i.addLabel('DTS:X', locked=False)
                    if hdr_banner == False:
                        if 'Dolby Vision' in hdr and config[0].new_hdr == 1:
                            dolby_vision(tmp_poster)
                        elif "HDR10+" in hdr and config[0].new_hdr == 1:
                            hdr10(tmp_poster)
                        elif hdr == "None":
                            pass
                        elif (
                            hdr != ""
                            and config[0].new_hdr == 1
                        ):
                            hdrp(tmp_poster)
                    elif 'Dolby Vision' in hdr:
                        i.addLabel('Dolby Vision', locked=False)
                    elif 'HDR10+' in hdr:
                        i.addLabel('HDR10+', locked=False)
                    elif hdr != '':
                        i.addLabel('HDR', locked=False)                

                audio_hdr = database_decision(r)
                audio = audio_hdr[0]
                hdr = audio_hdr[1]
                banner_decision()

            if res == '4k' and config[0].films4kposters == 1:
                if wide_banner == mini_banner == False:
                    add_banner(tmp_poster)
                else:
                    logger.debug(i.title+' Has banner') 
            rechk_banners = check_banners(tmp_poster)
            if True not in rechk_banners:
                try:
                    os.remove(tmp_poster)
                except:
                    pass
        def check_for_new_poster(tmp_poster):
            if r:
                new_poster = 'False'
                try:
                    poster_file = r[0].poster
                    try:
                        bak_poster = Image.open(poster_file)
                        bak_poster_hash = imagehash.average_hash(bak_poster)
                        poster = Image.open(tmp_poster)
                        poster_hash = imagehash.average_hash(poster)
                    except SyntaxError as e:
                        logger.error(repr(e))
                    except OSError as e:
                        logger.error(e)
                        if 'FileNotFoundError'  or 'Errno 2 'in e:
                            logger.debug(i.title+' - Poster Not found')
                            shutil.copy(tmp_poster, poster_file)
                            new_poster = 'True'
                            return new_poster
                        else:
                            logger.debug(i.title)
                            logger.warning(repr(e))
                            ImageFile.LOAD_TRUNCATED_IMAGES = True
                            bak_poster = Image.open(poster_file)
                            bak_poster_hash = imagehash.average_hash(bak_poster)
                            poster = Image.open(tmp_poster)
                            poster_hash = imagehash.average_hash(poster)
                            ImageFile.LOAD_TRUNCATED_IMAGES = False

                         
                    if poster_hash - bak_poster_hash > cutoff:
                        logger.debug(i.title+' - Poster has changed')
                        shutil.copy(tmp_poster, poster_file)
                        new_poster = 'True'
                        return new_poster                      
                    else:
                        logger.debug('Poster has not changed')
                        return new_poster
                        
                    
                except:
                    pass

        def get_poster():
            logger.debug(i.title+' Getting poster')
            imgurl = i.posterUrl
            img = requests.get(imgurl, stream=True)
            filename = tmp_poster
            try:
                if img.status_code == 200:
                    img.raw.decode_content = True
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(img.raw, f)
                    return tmp_poster 
                else:
                    logger.info("4k Posters: "+films.title+ 'cannot find the poster for this film')
            except OSError as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)

        for i in films.search(title=''):
            logger.info(i.title)           
            title = i.title
            guid = str(i.guid)
            guids = str(i.guids)
            size = i.media[0].parts[0].size
            res = i.media[0].videoResolution    
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
            tmp_poster = get_poster()     
            r = film_table.query.filter(film_table.guid == guid).all()
            try:
                if r[0].checked == 1:
                    logger.info(i.title+' has been checked, checking to see if file has changed')
                    if str(r[0].size) == str(size):
                        logger.info(title+' has been processed and the file has not changed, skiping')
                        new_poster = check_for_new_poster(tmp_poster)
                        print(new_poster)
                        if new_poster == 'True':
                            banners = check_banners(tmp_poster)
                            decision_tree(tmp_poster)
                            upload_poster(tmp_poster)
                    else:
                        logger.debug(i.title+' Checking for Banners')
                        banners = check_banners(tmp_poster)
                        decision_tree(tmp_poster)
                        upload_poster(tmp_poster)
                else:
                    logger.debug(i.title+' Checking for Banners')

                    check_for_new_poster(tmp_poster)                    
                    banners = check_banners(tmp_poster)
                    decision_tree(tmp_poster)
                    upload_poster(tmp_poster)
            except: 
                logger.debug('Poster retrieved')
                check_for_new_poster(tmp_poster)
                banners = check_banners(tmp_poster)
                decision_tree(tmp_poster)
                upload_poster(tmp_poster)
        dirpath = '/tmp/'
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                if file.endswith('.png'):
                    os.remove(dirpath+file)       
        logger.info('4k Poster script has finished')
    lib = config[0].filmslibrary.split(',')
    logger.debug(lib)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass    

def tv_episode_poster():
    from app.models import Plex, ep_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tv = plex.library.section('TV Programmes')
    banner_4k = Image.open("app/img/tv/4k.png")
    banner_bg = Image.open("app/img/tv/Background.png")
    banner_dv = Image.open("app/img/tv/dolby_vision.png")
    banner_hdr10 = Image.open("app/img/tv/hdr10.png")
    banner_new_hdr = Image.open("app/img/tv/hdr.png")
    atmos = Image.open("app/img/tv/atmos.png")
    dtsx = Image.open("app/img/tv/dtsx.png")
    size = (1280,720)
    box_4k= (52,68,275,225)
    hdr_box = (32,442,307,561)
    a_box = (32,562,307,681)
    cutoff = 10
    tmdb.api_key = config[0].tmdb_api
    tv = plex.library.section('TV Programmes')    
    logger.info('Starting 4k Tv poster script')
    def add_background(tmp_poster):
        background = Image.open(tmp_poster)
        logger.debug(img_title+' Adding background')
        background.paste(banner_bg, (0, 0), banner_bg)
        background.save(tmp_poster)
    def add_banner(tmp_poster):
        background = Image.open(tmp_poster)
        logger.debug(img_title+' Adding 4k banner')
        background.paste(banner_4k, (0, 0), banner_4k)
        background.save(tmp_poster)
    def hdrp(tmp_poster):
        logger.debug(img_title+" Adding HDR Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
        background.save(tmp_poster)
    def dolby_vision(tmp_poster):
        logger.debug(img_title+" Adding Dolby Vision Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_dv, (0, 0), banner_dv)
        background.save(tmp_poster)
    def hdr10(tmp_poster):
        logger.debug(img_title+" Adding HDR10+ banner")
        background = Image.open(tmp_poster)
        background.paste(banner_hdr10, (0, 0), banner_hdr10)
        background.save(tmp_poster)
    def atmos_poster(tmp_poster):
        logger.debug(img_title+' Adding Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(atmos, (0, 0), atmos)
        background.save(tmp_poster)   
    def dtsx_poster(tmp_poster):
        logger.debug(img_title+' Adding Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(dtsx, (0, 0), dtsx)
        background.save(tmp_poster)  

    def check_banners(tmp_poster):
        size = (1280,720)
        logger.debug(img_title+' Checking for Banners')
        try:
            background = Image.open(tmp_poster)
            background = background.resize(size,Image.LANCZOS)
        except OSError as e:
            logger.error(e)
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            background = background.resize(size,Image.LANCZOS)
            ImageFile.LOAD_TRUNCATED_IMAGES = False
    
        # 4K banner box
        bannerchk = background.crop(box_4k)
        # Audio Box
        audiochk = background.crop(a_box)
        # HDR Box
        hdrchk = background.crop(hdr_box)
    
        # POSTER HASHES
        # 4K Banner
        poster_banner_hash = imagehash.average_hash(bannerchk)
        # Audio Banner
        poster_audio_hash = imagehash.average_hash(audiochk)
        # HDR Banner
        poster_hdr_hash = imagehash.average_hash(hdrchk)
    
        # General Hashes
        chk_4k = Image.open("app/img/tv/chk_4k.png")
        chk_banner_hash = imagehash.average_hash(chk_4k)
    
        chk_hdr = Image.open("app/img/tv/chk_hdr.png")
        chk_hdr_hash = imagehash.average_hash(chk_hdr)
    
        chk_dolby_vision = Image.open("app/img/tv/chk_dv.png")
        chk_dolby_vision_hash = imagehash.average_hash(chk_dolby_vision)
    
        chk_hdr10 = Image.open("app/img/tv/chk_hdr10.png")
        chk_hdr10_hash = imagehash.average_hash(chk_hdr10)
    
        atmos_box = Image.open("app/img/tv/chk_atmos.png")
        chk_atmos_hash = imagehash.average_hash(atmos_box)
    
        dtsx_box = Image.open("app/img/tv/chk_dts.png")
        chk_dtsx_hash = imagehash.average_hash(dtsx_box)
    
        banner_4k = audio_banner = hdr_banner = False
    
        if poster_banner_hash - chk_banner_hash < cutoff:
            banner_4k = True
        if (
            poster_audio_hash - chk_atmos_hash < cutoff
            or poster_audio_hash - chk_dtsx_hash < cutoff
        ):
            audio_banner = True
        if (
            poster_hdr_hash - chk_hdr_hash < cutoff 
            or poster_hdr_hash - chk_dolby_vision_hash < cutoff 
            or poster_hdr_hash - chk_hdr10_hash < cutoff
        ):
            hdr_banner = True
        background.save(tmp_poster)
        return banner_4k, audio_banner, hdr_banner

    def backup_poster(tmp_poster):
        import random
        import string
        fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
        logger.debug(ep.title+" No banners detected so adding backup file to database")
        try:
            if r[0].poster:
                b_file = r[0].poster
            else:
                b_file = b_dir+'tv/episodes/'+fname+'.png'
        except:
            b_file = b_dir+'tv/episodes/'+fname+'.png'
        shutil.copy(tmp_poster, b_file)
        return b_file

    def scan_files():
        logger.debug('Scanning '+img_title)
        file = re.sub(config[0].plexpath, '/films', ep.media[0].parts[0].file)
        m = MediaInfo.parse(file, output='JSON')
        x = json.loads(m)
        #print(x)
        hdr_version = get_plex_hdr()
        if hdr_version != 'None':
            try:
                hdr_version = x['media']['track'][1]['HDR_Format_String']
            except:
                if "dolby" not in str.lower(hdr_version):
                    try:
                        hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
                    except:
                        try:
                            hdr_version = x['media']['track'][1]['HDR_Format_Commercial_IfAny']
                        except:
                            pass
        audio = ""
        try:
            while True:
                for f in range(5):
                    if 'Audio' in x['media']['track'][f]['@type']:
                        if 'Format_Commercial_IfAny' in x['media']['track'][f]:
                            audio = x['media']['track'][f]['Format_Commercial_IfAny']
                            if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                                audio = 'DTS:X'
                            break
                        elif 'Format' in x['media']['track'][f]:
                            audio = x['media']['track'][f]['Format']
                            break
                else:
                    break
                if audio != "":
                    break
        except Exception as e:
            pass
        return audio, hdr_version

    def upload_poster(tmp_poster):
        if os.path.exists(tmp_poster) == True:
            ep.uploadPoster(filepath=tmp_poster)
        else:
            print('ERROR no file detected')                    

    def insert_intoTable(hdr, audio, b_file, banners):           
         
        logger.debug(ep.title+' '+hdr+' '+audio)  
        #b_file = backup_poster(tmp_poster)
        b_file = re.sub('/config', 'static', b_file)
        if True not in banners:
            logger.debug('Adding '+ep.title+' to database')
            episode = ep_table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file, checked='1')
            db.session.add(episode)
            db.session.commit()

    def updateTable(hdr, audio, b_file, banners):
        logger.debug('Updating '+ep.title+' in database')
        logger.debug(ep.title+' '+hdr+' '+audio)   
        #b_file = backup_poster(tmp_poster)
        b_file = re.sub('/config', 'static', b_file)
        if True not in banners:
            row = r[0].id
            film = ep_table.query.get(row)
            film.size = size
            film.res = res
            film.hdr = hdr
            film.audio = audio
            film.poster = b_file
            film.checked = '1'
            db.session.commit()

    def get_plex_hdr():
        ekey = ep.key
        m = plex.fetchItems(ekey)
        for m in m:
            try:
                if m.media[0].parts[0].streams[0].DOVIPresent == True:
                    hdr_version='Dolby Vision'
                    ep.addLabel('Dolby Vision', locked=False)
                elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                    hdr_version='HDR'
                    ep.addLabel('HDR', locked=False)
                else:
                    hdr_version = 'None'
                return hdr_version
            except IndexError:
                pass

    def decision_tree(tmp_poster):
        banners = check_banners(tmp_poster)
        banner_4k = banners[0]
        audio_banner = banners[1]
        hdr_banner = banners[2]
    
        logger.debug(banners)
        def database_decision(r):
            if r:
                if r[0].poster:
                    b_file = r[0].poster
                else:
                    b_file = backup_poster(tmp_poster)

                audio = r[0].audio
                hdr= r[0].hdr
                if str(r[0].guid) == guid:
                    logger.debug(title+' GUID match')
                    if str(r[0].size) != size:
                            logger.debug(title+" has changed, rescanning")
                            scan = scan_files()
                            audio = scan[0]
                            hdr = scan[1]                             
                            updateTable(hdr, audio, b_file, banners)
                    else:
                        updateTable(hdr, audio, b_file, banners)
                        
                    if not r[0].poster and True not in banners:
                        updateTable(hdr, audio, b_file, banners)
                    else:
                        logger.debug(title+' is the same')
                else:
                    scan = scan_files()
                    audio = scan[0]
                    hdr = scan[1]
                    logger.debug(hdr)
                    if hdr == "":
                        hdr = get_plex_hdr()
                    updateTable(hdr, audio, b_file, banners)
            else:
                logger.debug('File not in Database')
                scan = scan_files()
                audio = scan[0]
                hdr = scan[1]
                b_file = backup_poster(tmp_poster)
                try:
                    insert_intoTable(hdr, audio, b_file, banners)
                except Exception as e:
                    logger.warning(repr(e))
                    #updateTable(hdr, audio, b_file, banners)
            
            def banner_decision(audio, hdr):
                if True not in banners:
                    logger.debug('creating backup')
                #    backup_poster(tmp_poster)
                    add_background(tmp_poster)

                if resolution == '4k' and banner_4k == False:
                    add_banner(tmp_poster)
                elif resolution != '4k' and banner_4k == False:
                    logger.debug(img_title+' does not need 4k banner') 
                elif resolution == '4k' and banner_4k != False:
                    logger.debug(img_title+' has 4k banner')

                if (
                audio_banner == False 
                and config[0].audio_posters == 1
                ) or (
                hdr_banner == False
                and config[0].hdr ==1
                ):

                    if audio_banner == False:
                        if 'Atmos' in audio and config[0].audio_posters == 1:
                            atmos_poster(tmp_poster)
                        elif audio == 'DTS:X' and config[0].audio_posters == 1:
                            dtsx_poster(tmp_poster)

                #    elif 'Atmos' in audio:
                #        ep.addLabel('Dolby Atmos', locked=False)
                #    elif audio == 'DTS:X':
                #        ep.addLabel('DTS:X', locked=False)
                    if hdr_banner == False:
                        try:
                            if 'dolby vision' in hdr and config[0].hdr == 1:
                                dolby_vision(tmp_poster)
                            elif "hdr10+" in hdr and config[0].hdr == 1:
                                hdr10(tmp_poster)
                            elif hdr != "" and config[0].hdr == 1:
                                hdrp(tmp_poster)
                        except:
                            pass
                #    elif 'dolby vision' in hdr_version:
                #        ep.addLabel('Dolby Vision', locked=False)
                #    elif 'hdr10+' in hdr_version:
                #        ep.addLabel('HDR10+', locked=False)
                #    elif hdr_version != '':
                #        ep.addLabel('HDR', locked=False)
            banner_decision(audio, hdr)
        database_decision(r)             

        if res == '4k' and config[0].films4kposters == 1:
            if banner_4k == False:
                add_banner(tmp_poster)
            else:
                logger.debug(ep.title+' Has banner') 
        rechk_banners = check_banners(tmp_poster)
        if True not in rechk_banners:
            try:
                os.remove(tmp_poster)
            except:
                pass

    def check_for_new_poster(tmp_poster):
        if r:
            new_poster = 'False'
            try:
                poster_file = r[0].poster
                try:
                    bak_poster = Image.open(poster_file)
                    bak_poster_hash = imagehash.average_hash(bak_poster)
                    poster = Image.open(tmp_poster)
                    poster_hash = imagehash.average_hash(poster)
                except SyntaxError as e:
                    logger.error(repr(e))
                except OSError as e:
                    logger.error(e)
                    if 'FileNotFoundError'  or 'Errno 2 'in e:
                        logger.debug(ep.title+' - Poster Not found')
                        shutil.copy(tmp_poster, poster_file)
                        new_poster = 'True'
                        return new_poster
                    else:
                        logger.debug(ep.title)
                        logger.warning(repr(e))
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        bak_poster = Image.open(poster_file)
                        bak_poster_hash = imagehash.average_hash(bak_poster)
                        poster = Image.open(tmp_poster)
                        poster_hash = imagehash.average_hash(poster)
                        ImageFile.LOAD_TRUNCATED_IMAGES = False

                     
                if poster_hash - bak_poster_hash > '15':
                    logger.debug(ep.title+' - Poster has changed')
                    shutil.copy(tmp_poster, poster_file)
                    new_poster = 'True'
                    return new_poster                      
                else:
                    logger.debug('Poster has not changed')
                    return new_poster
                    
                
            except:
                pass
        else:
            logger.debug("File not in database, doesn't need checking")
            pass

    def get_poster():
        logger.debug(img_title+' Getting poster')
        imgurl = ep.posterUrl
        img = requests.get(imgurl, stream=True)
        filename = tmp_poster
        try:
            if img.status_code == 200:
                img.raw.decode_content = True
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(img.raw, f)
                return tmp_poster 
            else:
                logger.info("4k TV Posters: "+ep.grandparentTitle+ 'cannot find the poster for this film')
        except OSError as e:
            logger.error(e)



    for ep in tv.search(libtype='episode'):
        img_title = ep.grandparentTitle+"_"+ep.parentTitle+"_"+ep.title
        resolution = ep.media[0].videoResolution
        hdr = get_plex_hdr()
        if resolution == '4k' or hdr != 'None':
            title = ep.title
            guid = str(ep.guid)
            guids = str(ep.guids)
            size = ep.media[0].parts[0].size
            res = ep.media[0].videoResolution    
            img_title = re.sub(r'[\\/*?:"<>| ]', '_', img_title)
            tmp_poster = re.sub(' ','_', '/tmp/'+img_title+'_poster.png')
            tmp_poster = get_poster()
            r = ep_table.query.filter(ep_table.guid == guid).all()
            try:
                if r[0].checked == 1:
                    logger.info(ep.title+' has been checked, checking to see if the file has    changed')
                    if str(r[0].size) == str(size):
                            logger.info(title+' has been processed and the file has not hanged, skiping scan')
                            new_poster = check_for_new_poster(tmp_poster)
                            if new_poster == 'True':
                                #banners = check_banners(tmp_poster)
                                decision_tree(tmp_poster)
                                upload_poster(tmp_poster)
                    else:
                        #logger.debug(ep.title+' Checking for Banners')
                        #banners = check_banners(tmp_poster)
                        decision_tree(tmp_poster)
                        upload_poster(tmp_poster)
                else:
                    #logger.debug(ep.title+' Checking for Banners')
                    check_for_new_poster(tmp_poster)                    
                    #banners = check_banners(tmp_poster)
                    decision_tree(tmp_poster)
                    upload_poster(tmp_poster)
            except IndexError: 
                check_for_new_poster(tmp_poster)
                #banners = check_banners(tmp_poster)
                decision_tree(tmp_poster)
                upload_poster(tmp_poster)                    
        else:
            logger.debug('Skipping: '+img_title)

def restore_episodes_from_database():
    from app.models import Plex, ep_table
    from app import db
    from tmdbv3api import TMDb, Search, Movie, Discover, TV, Episode
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tv = plex.library.section('TV Programmes')
    tmdb = TMDb()
    poster_url_base = 'https://www.themoviedb.org/t/p/original'
    search = Search()
    movie = Movie()
    tmdbtv = Episode()
    discover = Discover()
    tmdb.api_key = config[0].tmdb_api
    def restore_tmdb():
        logger.info("RESTORE: restoring posters from TheMovieDb")
        def get_tmdb_guid():
            g = [s for s in tv.search(libtype='show', guid=i.grandparentGuid)]
            g = str(g[0].guids)
            print(g)
            #g = str(r[0].guids)
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
        tmdb_search = tmdbtv.details(tv_id=g, episode_num= episode, season_num=season)
        logger.info(i.title)
        #print(tmdb_search)
        def get_poster(poster):
            r = requests.get(poster_url_base+poster, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open('tmdb_poster_restore.png', 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                    i.uploadPoster(filepath='tmdb_poster_restore.png')
                    os.remove('tmdb_poster_restore.png')
        try:
            poster = tmdb_search.still_path
            get_poster(poster) 
        except TypeError:
            logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
            pass

    for i in tv.search(libtype='episode'):
        title = i.title
        guid = str(i.guid)
        logger.info('restoring '+title)
        logger.debug(guid)
        season = str(i.parentIndex)
        episode = str(i.index)
        print(i.grandparentTitle+' '+season+' '+episode)
        r = ep_table.query.filter(ep_table.guid == guid).all()
        if r:
            resolution = i.media[0].videoResolution
            hdr = r[0].hdr
            if (resolution == '4k' or hdr != 'None'):
                try:
                    b_file = r[0].poster
                    b_file = re.sub('static', '/config', b_file)
                    if b_file:
                        i.uploadPoster(filepath=b_file)
                    else:
                        restore_tmdb()
                    row = r[0].id
                    film = ep_table.query.get(row)
                    film.checked = '0'
                    db.session.commit()
                except (TypeError, IndexError, FileNotFoundError) as e:
                    logger.error(repr(e))  

def restore_episode_from_database(var):
    from app.models import Plex, ep_table
    from app import db
    from tmdbv3api import TMDb, Search, Movie, Discover, TV, Episode
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tv = plex.library.section('TV Programmes')
    tmdb = TMDb()
    poster_url_base = 'https://www.themoviedb.org/t/p/original'
    search = Search()
    movie = Movie()
    tmdbtv = Episode()
    discover = Discover()
    tmdb.api_key = config[0].tmdb_api
    def restore_tmdb():
        logger.info("RESTORE: restoring posters from TheMovieDb")
        def get_tmdb_guid():
            g = [s for s in tv.search(libtype='show', guid=i.grandparentGuid)]
            g = str(g[0].guids)
            print(g)
            #g = str(r[0].guids)
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
        tmdb_search = tmdbtv.details(tv_id=g, episode_num= episode, season_num=season)
        logger.info(i.title)
        #print(tmdb_search)
        def get_poster(poster):
            r = requests.get(poster_url_base+poster, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open('tmdb_poster_restore.png', 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                    i.uploadPoster(filepath='tmdb_poster_restore.png')
                    os.remove('tmdb_poster_restore.png')
        try:
            poster = tmdb_search.still_path
            get_poster(poster) 
        except TypeError:
            logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
            pass

    for i in tv.search(libtype='episode', guid=var):
        title = i.title
        guid = str(i.guid)
        logger.info('restoring '+title)
        logger.debug(guid)
        season = str(i.parentIndex)
        episode = str(i.index)
        print(i.grandparentTitle+' '+season+' '+episode)
        r = ep_table.query.filter(ep_table.guid == guid).all()
        if r:
            resolution = i.media[0].videoResolution
            hdr = r[0].hdr
            if (resolution == '4k' or hdr != 'None'):
                try:
                    b_file = r[0].poster
                    b_file = re.sub('static', '/config', b_file)
                    if b_file:
                        i.uploadPoster(filepath=b_file)
                    else:
                        restore_tmdb()
                    row = r[0].id
                    film = ep_table.query.get(row)
                    film.checked = '0'
                    db.session.commit()
                except (TypeError, IndexError, FileNotFoundError) as e:
                    logger.error(repr(e))  

def posters3d(): 
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api

    plex = PlexServer(config[0].plexurl, config[0].token)
    films = plex.library.section(config[0].library3d)
    if config[0].posters3d == 1:


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
            elif config[0].mini3d == 1:
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
            newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')
            imgurl = i.posterUrl
            img = requests.get(imgurl, stream=True)
            if img.status_code == 200:
                img.raw.decode_content = True
                filename = "/tmp/poster.png"

                with open(filename, 'wb') as f:
                    shutil.copyfileobj(img.raw, f)
                if config[0].backup == 1: 
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
                            shutil.copyfile(filename, newdir+'poster_bak.png')
                    else:        
                        logger.info('3D Posters: Creating a backup file')
                        shutil.copyfile(filename, newdir+'poster_bak.png')
            else:
                logger.warning("3D Posters: "+films.title+" cannot find the poster for this film")   

        for i in films.search():
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
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

def restore_posters():
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api

    plex = PlexServer(config[0].plexurl, config[0].token)
    def run_script():

        
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
            def restore():
                    logger.info("RESTORE: restoring posters from Local Backups")
                    poster = newdir+'poster_bak.png'
                    logger.info(i.title+ ' Restored')
                    i.uploadPoster(filepath=poster)


            for i in films.search():
                i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
                newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
                backup = os.path.exists(newdir+'poster_bak.png')
                if backup == True:
                    try:
                        restore()
                    except OSError as e:
                        if e.errno == 2:
                            logger.debug(e)

                elif config[0].tmdb_restore == 1 and backup == False:
                    def get_poster():
                        logger.debug(i.title+' Getting poster')
                        imgurl = i.posterUrl
                        img = requests.get(imgurl, stream=True)
                        filename = tmp_poster
                        try:
                            if img.status_code == 200:
                                img.raw.decode_content = True
                                with open(filename, 'wb') as f:
                                    shutil.copyfileobj(img.raw, f)
                                return tmp_poster 
                            else:
                                logger.info("4k Posters: "+films.title+ 'cannot find the poster for             this film')
                        except OSError as e:
                            logger.error(e)
                        except Exception as e:
                            logger.error(e)
                    def check_banners(tmp_poster):
                        size = (911,1367)
                        try:
                            background = Image.open(tmp_poster)
                            background = background.resize(size,Image.LANCZOS)
                        except OSError as e:
                            logger.error(e)
                            ImageFile.LOAD_TRUNCATED_IMAGES = True
                            background = background.resize(size,Image.LANCZOS)
                            ImageFile.LOAD_TRUNCATED_IMAGES = False

                        # Wide banner box
                        bannerchk = background.crop(bannerbox)
                        # Mini Banner Box
                        minichk = background.crop(mini_box)
                        # Audio Box
                        audiochk = background.crop(a_box)
                        # HDR Box
                        hdrchk = background.crop(hdr_box)

                        # POSTER HASHES
                        # Wide Banner
                        poster_banner_hash = imagehash.average_hash(bannerchk)
                        # Mini Banner
                        poster_mini_hash = imagehash.average_hash(minichk)
                        # Audio Banner
                        poster_audio_hash = imagehash.average_hash(audiochk)
                        # HDR Banner
                        poster_hdr_hash = imagehash.average_hash(hdrchk)

                        # General Hashes
                        chk_banner = Image.open("app/img/chk-4k.png")
                        chk_banner_hash = imagehash.average_hash(chk_banner)

                        chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
                        chk_mini_banner_hash = imagehash.average_hash(chk_mini_banner)

                        chk_hdr = Image.open("app/img/chk_hdr.png")
                        chk_hdr_hash = imagehash.average_hash(chk_hdr)

                        chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
                        chk_dolby_vision_hash = imagehash.average_hash(chk_dolby_vision)

                        chk_hdr10 = Image.open("app/img/chk_hdr10.png")
                        chk_hdr10_hash = imagehash.average_hash(chk_hdr10)

                        chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
                        chk_new_hdr_hash = imagehash.average_hash(chk_new_hdr)

                        atmos_box = Image.open("app/img/chk_atmos.png")
                        chk_atmos_hash = imagehash.average_hash(atmos_box)

                        dtsx_box = Image.open("app/img/chk_dtsx.png")
                        chk_dtsx_hash = imagehash.average_hash(dtsx_box)

                        wide_banner = mini_banner = audio_banner = hdr_banner = old_hdr = False

                        if poster_banner_hash - chk_banner_hash < cutoff:
                            wide_banner = True
                        if poster_mini_hash - chk_mini_banner_hash < cutoff:
                            mini_banner = True
                        if (
                            poster_audio_hash - chk_atmos_hash < cutoff
                            or poster_audio_hash - chk_dtsx_hash < cutoff
                        ):
                            audio_banner = True
                        if poster_hdr_hash - chk_hdr_hash < cutoff:
                            old_hdr = True
                        if (
                            poster_hdr_hash - chk_new_hdr_hash < cutoff 
                            or poster_hdr_hash - chk_dolby_vision_hash < cutoff 
                            or poster_hdr_hash - chk_hdr10_hash < cutoff
                        ):
                            hdr_banner = True
                        background.save(tmp_poster)
                        return wide_banner, mini_banner, audio_banner, hdr_banner, old_hdr                    
                    t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
                    tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                    tmp_poster = get_poster() 
                    banners = check_banners(tmp_poster)
                    if True in banners:
                        restore_tmdb()

        def check_connection():
            try:
                plex = PlexServer(config[0].plexurl, config[0].token)
            except requests.exceptions.ConnectionError as e:
                logger.error(e)
                logger.error('Cannot connect to your plex server. Please double check your config is correct.')
            else:
                continue_restore()                
        check_connection()
        
        for i in films.search():
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
            newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.join(newdir+'poster_bak.png')            
            try:
                os.remove(backup)
            except PermissionError as e:
                logger.error(e)
            except FileNotFoundError as e:
                logger.error(e)
        
    lib = config[0].filmslibrary.split(',')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass        
    logger.info('Restore Completed.')

def restore_from_database():
    from app.models import Plex, film_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    films = plex.library.section('Films')
    def convert_data(data, file_name):
        with open(file_name, 'wb') as file:
            file.write(data)
            

    for i in films.search():
        title = i.title
        guid = str(i.guid)
        logger.info('restoring '+title)
        logger.debug(guid)
        newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/poster_bak.png'
        r = film_table.query.filter(film_table.guid == guid).all()
        try:
            b_file = r[0].poster
            i.uploadPoster(filepath=b_file)
            row = r[0].id
            film = film_table.query.get(row)
            film.checked = '0'
            db.session.commit()
        except (TypeError, IndexError, FileNotFoundError) as e:
            logger.error(repr(e))  

def restore_single(var):
    from app.models import Plex, film_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    films = plex.library.section('Films')

    for i in films.search(guid=var):
        title = i.title
        guid = var
        logger.info('restoring '+title)
        logger.debug(guid)
        r = film_table.query.filter(film_table.guid == guid).all()
        try:
            b_file = re.sub('static', '/config', r[0].poster)
            i.uploadPoster(filepath=b_file)
            row = r[0].id
            film = film_table.query.get(row)
            film.checked = '0'
            db.session.commit()
        except (TypeError, IndexError, FileNotFoundError) as e:
            logger.error(repr(e)) 

def hide4k():
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api
    def run_script():

        if config[0].hide4k == 1:


            logger.info("Hide-4K: Hide 4k films script starting now")


            added = films.search(resolution='4k', sort='addedAt')
            b = films.search('untranscodable', sort='addedAt')
            def add_untranscodable():
                for movie in added:
                    resolutions = {m.videoResolution for m in movie.media}
                    if len(resolutions) < 2 and '4k' in resolutions:
                        if config[0].transcode == 0:
                            movie.addLabel('Untranscodable')   
                            logger.info("Hide-4K: "+movie.title+' has only 4k avaialble, setting untranscodable' )
                        elif config[0].transcode == 1:
                            logger.info('Hide-4K: Sending '+ movie.title+ ' to be transcoded')
                            movie.optimize(deviceProfile="Android", videoQuality=10)
            def remove_untranscodable():
                for movie in b:
                    resolutions = {m.videoResolution for m in movie.media}
                    if len(resolutions) > 1 and '4k' in resolutions:
                        movie.removeLabel('Untranscodable')
                        logger.info("Hide-4K: "+movie.title+ ' removing untranscodable label')
            add_untranscodable()
            remove_untranscodable()
            logger.info("Hide-4K: Hide 4K Script has finished.")
        else:
            logger.warning('Hide 4K films is not enabled in the config so will not run')  
    lib = config[0].filmslibrary.split(',')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass               

def fresh_hdr_posters():
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api

    plex = PlexServer(config[0].plexurl, config[0].token)
    films = plex.library.section(config[0].filmslibrary)
    def continue_fresh_posters():
        logger.info("Restore-posters: Restore backup posters starting now") 
        for i in films.search(hdr='true'):
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')  
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
            
            newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png') 
            if backup == True:
                poster = newdir+'poster_bak.png'
                logger.info(i.title+ ' Restored from Local files')
                i.uploadPoster(filepath=poster)
                os.remove(poster)
            elif config[0].tmdb_restore == 1 and backup == False:
                restore_tmdb()
        posters4k()
    def check_connection():
        try:
            plex = PlexServer(config[0].plexurl, config[0].token)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            logger.error('Cannot connect to your plex server. Please double check your config is correct.')
        else:
            continue_fresh_posters()
    check_connection()

def autocollections():
    logger.info('Autocollections has started')
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api

    plex = PlexServer(config[0].plexurl, config[0].token)

    def run_script():
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
            if config[0].tautulli_api != '':
                try:
                    tautulli_api = RawAPI(base_url=config[0].tautulli_server, api_key=config[0].tautulli_api)
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
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': 'Marvel Studios'})
                    d = films.collection(collection)
                    d.uploadPoster(filepath='/tmp/poster.png')
                if config[0].default_poster == 1:
                    c.uploadPoster(filepath='app/img/collections/mcu_poster.png')
            except plexapi.exceptions.NotFound:
                plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': 'Marvel Studios'})
                d = films.collection(collection)
                if config[0].default_poster == 1:
                    d.uploadPoster(filepath='app/img/collections/mcu_poster.png') 
            logger.info("MCU Collection has finished")
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
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': collection})
                    d = films.collection(collection)
                    d.uploadPoster(filepath='/tmp/poster.png')
                if config[0].default_poster == 1:
                    c.uploadPoster(filepath='app/img/collections/pixar_poster.jpeg')                    
            except plexapi.exceptions.NotFound:
                plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': collection})
                d = films.collection(collection)
                if config[0].default_poster == 1:
                    d.uploadPoster(filepath='app/img/collections/pixar_poster.jpeg')
            logger.info("Pixar Collection has finished")
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
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': collection})
                    d = films.collection(collection)
                    d.uploadPoster(filepath='/tmp/poster.png')
                if config[0].default_poster == 1:
                    c.uploadPoster(filepath='app/img/collections/disney_poster.jpeg') 
            except plexapi.exceptions.NotFound:
                plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'studio': collection})
                d = films.collection(collection)
                if config[0].default_poster == 1:
                    d.uploadPoster(filepath='app/img/collections/disney_poster.jpeg')
            logger.info("Disney Collection has finished")
        def audio_collections():
            def atmos():
                collection = 'Dolby Atmos'
                try:
                    c = films.collection(title=collection)
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'label': collection})
                    d = films.collection(collection)
                    if config[0].default_poster == 1:
                        d.uploadPoster(filepath='app/img/collections/Atmos_Poster.png') 
                logger.info("Dolby Atmos Collection has finished") 
            def dtsx():
                collection = 'DTS:X'
                try:
                    c = films.collection(title=collection)
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'label': collection})
                    d = films.collection(collection)
                    if config[0].default_poster == 1:
                        d.uploadPoster(filepath='app/img/collections/DTSX_Poster.png') 
                logger.info("DTS:X Collection has finished")
            atmos()
            dtsx()
        def HDR_collections():
            def dolby_vision():
                collection = 'Dolby Vision'
                try:
                    c = films.collection(title=collection)
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config[0].filmslibrary, title=collection, smart=True, filters={'label': collection})
                    d = films.collection(collection)
                    if config[0].default_poster == 1:
                        d.uploadPoster(filepath='app/img/collections/dolby_vision_Poster.png') 
                logger.info("Dolby Vision Collection has finished")
            dolby_vision() 
        if config[0].autocollections == 1:
            audio_collections()
            HDR_collections()
        if config[0].disney == 1:
            disney()
        if config[0].pixar == 1:
            pixar()
        if config[0].mcu_collection == 1:
            MCU()                
        if config[0].tr_r_p_collection == 1:
            popular()
            top_rated()
            recommended() 
        logger.info("Auto Collections has finished")
    lib = config[0].filmslibrary.split(',')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass        

def remove_unused_backup_files():
    from app.models import Plex
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    def run_script():

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
            newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
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
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            p = 'poster_bak.png'
            tmp_poster = re.sub(' ','_', '/tmp/poster.png')
            newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.exists(newdir+'poster_bak.png')
            b_poster = newdir+p
            if backup == True:
                get_poster()
                check_for_banner()
        try:
            os.remove(tmp_poster)
        except FileNotFoundError:
            pass  
        logger.info('Search complete')    
    lib = config[0].filmslibrary.split(',')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass

def test_script():
    logger.info('test script running')

def fill_database():
    from app.models import Plex, film_table
    from app import db
    config = Plex.query.filter()
    plex = PlexServer(config[0].plexurl, config[0].token)
    tmdb.api_key = config[0].tmdb_api
    def run_script():
        def main():
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
                            tmdb_poster = 'tmdb_poster_restore.png'
                            return tmdb_poster
                try:
                    poster = tmdb_search.poster_path
                    tmdb_poster = get_poster(poster) 
                    return tmdb_poster
                except TypeError:
                    logger.info("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")
                    pass                            
            def scan_files():
                    try:
                        logger.debug('Scanning '+i.title)
                        file = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
                        m = MediaInfo.parse(file, output='JSON')
                        x = json.loads(m)
                        hdr_version = get_plex_hdr()
                        try:
                            hdr_version = x['media']['track'][1]['HDR_Format_String']
                        except (KeyError, IndexError):
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
                                            if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                                                audio = 'DTS:X'
                                            break
                                        elif 'Format' in x['media']['track'][f]:
                                            audio = x['media']['track'][f]['Format']
                                            break
                                if audio != "":
                                    break
                        except (IndexError, KeyError) as e:
                            logger.debug(i.title+' '+repr(e))
                        return audio, hdr_version
                    except FileNotFoundError as e:
                        logger.error(repr(e))

            def insert_intoTable(hdr, audio, tmp_poster):
                if config[0].manualplexpath == 1:
                    newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
                else:
                    newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
                backup = os.path.exists(newdir+'poster_bak.png')            
                logger.debug('Adding '+i.title+' to database') 
                logger.debug(i.title+' '+hdr+' '+audio)  
                pblob = backup_poster(tmp_poster)
                b_file = re.sub('/config', 'static', pblob)
                if not r:
                    film = film_table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file)
                    db.session.add(film)   
                    db.session.commit()
                elif r[0].size != size:
                    updateTable(hdr, audio, tmp_poster)
             
            def updateTable(hdr, audio, tmp_poster):
                if config[0].manualplexpath == 1:
                    newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
                else:
                    newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
                backup = os.path.exists(newdir+'poster_bak.png')
                logger.debug('Updating '+i.title+' in database')
                logger.debug(i.title+' '+hdr+' '+audio)   
                pblob = backup_poster(tmp_poster)
                b_file = re.sub('/config', 'static', pblob)
                if backup == True or True not in banners:
                    row = r[0].id
                    film = film_table.query.get(row)
                    film.size = size
                    film.res = res
                    film.hdr = hdr
                    film.audio = audio
                    film.poster = b_file
                    db.session.commit()

            def backup_poster(tmp_poster):
                if config[0].manualplexpath == 1:
                    newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
                else:
                    newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
                old_backup = os.path.exists(newdir+'poster_bak.png')
                fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
                b_file = ''
                if old_backup == True:
                    bak_file = newdir+'poster_bak.png'
                    b_file = b_dir+'films/'+fname+'.png'
                    shutil.copy(bak_file, b_file)
                    #return b_file
                elif True not in banners:
                    logger.debug(i.title+" No banners detected so adding backup file to database")
                    #try:
                    #    if r[0].poster:
                    #        b_file = r[0].poster
                    #    else:
                    #        b_file = b_dir+'films/'+fname+'.png'
                    #except:
                    b_file = b_dir+'films/'+fname+'.png'
                    shutil.copy(tmp_poster, b_file)
                    #return b_file
                elif True in banners:
                    b_file = b_dir+'films/'+fname+'.png'
                    tmdb_poster = restore_tmdb()
                    shutil.copy(tmdb_poster, b_file)
                return b_file

            def check_banners(tmp_poster):

                banner_4k = Image.open("app/img/4K-Template.png")
                mini_4k_banner = Image.open("app/img/4K-mini-Template.png")
                banner_dv = Image.open("app/img/dolby_vision.png")
                banner_hdr10 = Image.open("app/img/hdr10.png")

                banner_new_hdr = Image.open("app/img/hdr.png")
                atmos = Image.open("app/img/atmos.png")
                dtsx = Image.open("app/img/dtsx.png")

                size = (911,1367)
                bannerbox= (0,0,911,100)
                mini_box = (0,0,150,125)
                hdr_box = (0,605,225,731)
                a_box = (0,731,225,803)

                cutoff = 10 

                logger.debug(i.title+' Checking for Banners')
                try:
                    background = Image.open(tmp_poster)
                    background = background.resize(size,Image.ANTIALIAS)
                except OSError as e:
                    logger.error(e)
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    background = background.resize(size,Image.ANTIALIAS)
                    ImageFile.LOAD_TRUNCATED_IMAGES = False

                # Wide banner box
                bannerchk = background.crop(bannerbox)
                # Mini Banner Box
                minichk = background.crop(mini_box)
                # Audio Box
                audiochk = background.crop(a_box)
                # HDR Box
                hdrchk = background.crop(hdr_box)

                # POSTER HASHES
                # Wide Banner
                poster_banner_hash = imagehash.average_hash(bannerchk)
                # Mini Banner
                poster_mini_hash = imagehash.average_hash(minichk)
                # Audio Banner
                poster_audio_hash = imagehash.average_hash(audiochk)
                # HDR Banner
                poster_hdr_hash = imagehash.average_hash(hdrchk)

                # General Hashes
                chk_banner = Image.open("app/img/chk-4k.png")
                chk_banner_hash = imagehash.average_hash(chk_banner)

                chk_mini_banner = Image.open("app/img/chk-mini-4k2.png")
                chk_mini_banner_hash = imagehash.average_hash(chk_mini_banner)

                chk_hdr = Image.open("app/img/chk_hdr.png")
                chk_hdr_hash = imagehash.average_hash(chk_hdr)

                chk_dolby_vision = Image.open("app/img/chk_dolby_vision.png")
                chk_dolby_vision_hash = imagehash.average_hash(chk_dolby_vision)

                chk_hdr10 = Image.open("app/img/chk_hdr10.png")
                chk_hdr10_hash = imagehash.average_hash(chk_hdr10)

                chk_new_hdr = Image.open("app/img/chk_hdr_new.png")
                chk_new_hdr_hash = imagehash.average_hash(chk_new_hdr)

                atmos_box = Image.open("app/img/chk_atmos.png")
                chk_atmos_hash = imagehash.average_hash(atmos_box)

                dtsx_box = Image.open("app/img/chk_dtsx.png")
                chk_dtsx_hash = imagehash.average_hash(dtsx_box)

                wide_banner = mini_banner = audio_banner = hdr_banner = old_hdr = False

                if poster_banner_hash - chk_banner_hash < cutoff:
                    wide_banner = True
                if poster_mini_hash - chk_mini_banner_hash < cutoff:
                    mini_banner = True
                if (
                    poster_audio_hash - chk_atmos_hash < cutoff
                    or poster_audio_hash - chk_dtsx_hash < cutoff
                ):
                    audio_banner = True
                if poster_hdr_hash - chk_hdr_hash < cutoff:
                    old_hdr = True
                if (
                    poster_hdr_hash - chk_new_hdr_hash < cutoff 
                    or poster_hdr_hash - chk_dolby_vision_hash < cutoff 
                    or poster_hdr_hash - chk_hdr10_hash < cutoff
                ):
                    hdr_banner = True
                background.save(tmp_poster)
                return wide_banner, mini_banner, audio_banner, hdr_banner, old_hdr
    
            def get_plex_hdr():
                ekey = i.key
                m = plex.fetchItems(ekey)
                for m in m:
                    try:
                        if m.media[0].parts[0].streams[0].DOVIPresent == True:
                            hdr_version='Dolby Vision'
                            i.addLabel('Dolby Vision', locked=False)
                        elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                            hdr_version='HDR'
                            i.addLabel('HDR', locked=False)
                        else:
                            hdr_version = 'None'
                        return hdr_version
                    except IndexError:
                        pass

            def get_poster():
                logger.debug(i.title+' Getting poster')
                imgurl = i.posterUrl
                img = requests.get(imgurl, stream=True)
                filename = tmp_poster
                try:
                    if img.status_code == 200:
                        img.raw.decode_content = True
                        with open(filename, 'wb') as f:
                            shutil.copyfileobj(img.raw, f)
                        return tmp_poster 
                    else:
                        logger.info("4k Posters: "+films.title+ 'cannot find the poster for this film')
                except OSError as e:
                    logger.error(e)
                    
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
            tmp_poster = get_poster()
            banners = check_banners(tmp_poster)
            logger.debug(banners)
            #backup_poster(tmp_poster)
            if config[0].skip_media_info == 1:
                hdr = get_plex_hdr()
                audio = ''
                insert_intoTable(hdr, audio, tmp_poster)
            else:
                try:
                    scan = scan_files()
                    audio = scan[0]
                    hdr = scan[1]
                    insert_intoTable(hdr, audio, tmp_poster)
                except:
                    logger.error('Can not scan '+title+': Please check your permissions. Looping back to Plex Metadata')
                    hdr = get_plex_hdr()
                    audio = ''
                    insert_intoTable(hdr, audio, tmp_poster)  
        for i in films.search():
            logger.debug(i.title)
            title = i.title
            guid = str(i.guid)
            guids = str(i.guids)
            size = i.media[0].parts[0].size
            res = i.media[0].videoResolution
            r = film_table.query.filter(film_table.guid == guid).all()
            if not r:
                main()
            else:
                if r[0].size != size:
                    logger.info(title+' is already in the database')
                else:
                    main()
                
        logger.debug('Database has been seeded')
        try:
            os.remove('tmdb_poster_restore.png')
        except:
            pass
    lib = config[0].filmslibrary.split(',')
    logger.debug(lib)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass 

def add_labels():

    from app.models import Plex, film_table
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)
    def run_script():
        logger.info('Adding Film Labels')
        for i in films.search(sort='random'):
            guid = str(i.guid)
            r = film_table.query.filter(film_table.guid == guid)
            logger.debug(i.title+" "+r[0].audio+" "+r[0].hdr)
            if 'Dolby Atmos' in r[0].audio:
                i.addLabel('Dolby Atmos', locked=False)  
            elif 'DTS:X' in r[0].audio:
                i.addLabel('DTS:X', locked=False)                
            if 'Dolby Vision' in r[0].hdr:
                i.addLabel('Dolby Vision', locked=False) 
            elif 'HDR10+' in r[0].hdr:
                i.addLabel('HDR10+', locked=False)
            elif 'HDR' in r[0].hdr:
                i.addLabel('HDR', locked=False)
        logger.info('Labels Added')
    lib = config[0].filmslibrary.split(',')
    logger.debug(lib)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass 

def maintenance():
    from app.models import Plex, film_table, ep_table
    from app import db
    config = Plex.query.filter(Plex.id == '1')
    plex = PlexServer(config[0].plexurl, config[0].token)

    def run_script(): 
        r = film_table.query.all()
        for f in r:
            #print(f.id)
            film = films.search(guid=f.guid)
            if film == "" or not film:
                print('deleting rows ',f.id)
                row = film_table.query.get(f.id)
                db.session.delete(row)
                db.session.commit()
                print('deleted rows')
        ep = ep_table.query.all()
        for e in ep:
            episode = tv.search(libtype='episode')
            if episode == "" or not episode:
                logger.warning('Deleting rows '+e.id)
                row = film_table.query.get(f.id)
                db.session.delete(row)
                db.session.commit()            
    lib = config[0].filmslibrary.split(',')
    logger.debug(lib)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass          
    tvlib = config[0].tvlibrary.split(',')
    logger.debug(lib)
    if len(tvlib) <= 2:
        try:
            while True:
                for l in range(10):
                    tv = plex.library.section(lib[l])
                    run_script()
        except IndexError:
            pass 

def collective4k():
    posters4k()
    from time import sleep
    sleep(5)
    logger.info('Starting 4k Tv poster script')
    tv_episode_poster()
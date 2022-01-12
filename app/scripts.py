
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
from requests.exceptions import ReadTimeout
from tmdbv3api import TMDb, Search, Movie, Discover
from pymediainfo import MediaInfo
import json
from tautulli.api import RawAPI
from flask_apscheduler import APScheduler
import unicodedata


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
discover = Discover()


def recently_added_posters(webhooktitle):
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]
    plex = PlexServer(config[0][1], config[0][2])
    lib = config[0][3].split(',')

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
    def hdr(tmp_poster):
        logger.debug(i.title+" HDR Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
        background.save(tmp_poster)
    def dolby_vision(tmp_poster):
        logger.debug(i.title+" Dolby Vision Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_dv, (0, 0), banner_dv)
        background.save(tmp_poster)
    def hdr10(tmp_poster):
        logger.debug(i.title+" HDR10+ banner")
        background = Image.open(tmp_poster)
        background.paste(banner_hdr10, (0, 0), banner_hdr10)
        background.save(tmp_poster)
    def atmos_poster(tmp_poster):
        logger.debug(i.title+' Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(atmos, (0, 0), atmos)
        background.save(tmp_poster)   
    def dtsx_poster(tmp_poster):
        logger.debug(i.title+' Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(dtsx, (0, 0), dtsx)
        background.save(tmp_poster)  
    def add_banner(tmp_poster):
        background = Image.open(tmp_poster)
        if config[0][14] == 1:
            logger.debug(i.title+' Adding Mini 4K Banner')
            background.paste(mini_4k_banner, (0,0), mini_4k_banner)
        else:
            logger.debug(i.title+' Adding 4k Banner')
            background.paste(banner_4k, (0, 0), banner_4k)
        background.save(tmp_poster)

    def check_banners(tmp_poster):
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

    def scan_files():
        logger.debug('Scanning '+i.title)
        file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
        m = MediaInfo.parse(file, output='JSON')
        x = json.loads(m)
        hdr_version = ""
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

    def restore_from_tmdb():
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

        def get_poster(poster_url):
            r = requests.get(poster_url_base+poster_url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open('/tmp/poster.png', 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        try:
            poster_url = tmdb_search.poster_path
            tmp_poster = get_poster(poster_url)
            return tmp_poster
        except TypeError:
            logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")



    def decision_tree(tmp_poster):
        banners = check_banners(tmp_poster)
        wide_banner = banners[0]
        mini_banner = banners[1]
        audio_banner = banners[2]
        hdr_banner = banners[3]
        old_hdr = banners[4]

        logger.debug(banners)
        resolution = i.media[0].videoResolution

        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            path = config[0][38]
            newdir = os.path.dirname(re.sub(config[0][5], path, i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        if old_hdr == True and config[0][28] == 1:
            if backup == True:
                tmp_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
            elif backup == False and config[0][26] == 1:
                tmp_poster = restore_from_tmdb()
        if (
        audio_banner == False 
        and config[0][35] == 1
        ) or (
        hdr_banner == False
        and config[0][15] ==1
        ):
            scanned = scan_files()
            audio = scanned[0]
            hdr_version = str.lower(scanned[1])
            if audio_banner == False:
                if 'Atmos' in audio and config[0][35] == 1:
                    atmos_poster(tmp_poster)
                elif audio == 'DTS:X' and config[0][35] == 1:
                    dtsx_poster(tmp_poster)

            elif 'Atmos' in audio:
                i.addLabel('Dolby Atmos', locked=False)
            elif audio == 'DTS:X':
                i.addLabel('DTS:X', locked=False)
            if hdr_banner == False:
                if 'dolby vision' in hdr_version and config[0][28] == 1:
                    dolby_vision(tmp_poster)
                elif "hdr10+" in hdr_version and config[0][28] == 1:
                    hdr10(tmp_poster)
                elif hdr_version != "" and config[0][28] == 1:
                    hdr(tmp_poster)
            elif 'dolby vision' in hdr_version:
                i.addLabel('Dolby Vision', locked=False)
            elif 'hdr10+' in hdr_version:
                i.addLabel('HDR10+', locked=False)
            elif hdr_version != '':
                i.addLabel('HDR', locked=False)
        if resolution == '4k' and config[0][24] == 1:
            if wide_banner == mini_banner == False:
                add_banner(tmp_poster)
            else:
                logger.debug(i.title+' Has banner')


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
                logger.warning("4k Posters: "+films.title+ 'cannot find the poster for this film')
        except OSError as e:
            logger.error(e)

    def backup_poster(tmp_poster):
        logger.debug(i.title+' Creating backup')
        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        shutil.copyfile(tmp_poster, newdir+'poster_bak.png')

    def check_for_new_poster(tmp_poster):
        logger.debug(i.title+' Checking for new poster')
        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            path = config[0][38]
            newdir = os.path.dirname(re.sub(config[0][5], path, i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        if backup == True:
            try:
                bak_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
                bak_poster_hash = imagehash.average_hash(bak_poster)
                poster = Image.open(tmp_poster)
                poster_hash = imagehash.average_hash(poster)
            except SyntaxError:
                logger.warning(i.title+' poster broken, restoring from TMDB')
                restore_from_tmdb()
            except OSError as e:
                logger.debug(i.title)
                logger.warning(repr(e))
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                bak_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
                bak_poster_hash = imagehash.average_hash(bak_poster)
                poster = Image.open(tmp_poster)
                poster_hash = imagehash.average_hash(poster)
                ImageFile.LOAD_TRUNCATED_IMAGES = False
            
            if poster_hash - bak_poster_hash > cutoff:
                logger.debug(i.title+' - Poster has changed')
                os.remove(os.path.join(newdir, 'poster_bak.png'))
        elif backup == False and config[0][12] == 1:
            try:
                backup_poster(tmp_poster)
            except PermissionError as e:
                logger.error(repr(e))

    logger.info('Webhook recieved for: '+webhooktitle)            
    
    def search_lib():
        logger.info('Starting 4K Poster script')
        for i in films.search(title=webhooktitle):
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
            logger.info(i.title)
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
            tmp_poster = get_poster()
            check_for_new_poster(tmp_poster)
            decision_tree(tmp_poster)
            if os.path.exists(tmp_poster) == True:
                try:
                    i.uploadPoster(filepath=tmp_poster)
                except ReadTimeout as e:
                    logger.error(repr(e))
                try:
                    os.remove(tmp_poster)
                except FileNotFoundError:
                    pass 
        logger.info('4k Poster script has finished')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    if config[0][13] == 1:
                        search_lib()
        except IndexError:
            pass    
        logger.info('4k Poster script has finished')
    else:
        logger.info('4K Posters script is disabled in config. ')

def posters4k():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]
    plex = PlexServer(config[0][1], config[0][2])
    lib = config[0][3].split(',')

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
    def hdr(tmp_poster):
        logger.debug(i.title+" HDR Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
        background.save(tmp_poster)
    def dolby_vision(tmp_poster):
        logger.debug(i.title+" Dolby Vision Banner")
        background = Image.open(tmp_poster)
        background.paste(banner_dv, (0, 0), banner_dv)
        background.save(tmp_poster)
    def hdr10(tmp_poster):
        logger.debug(i.title+" HDR10+ banner")
        background = Image.open(tmp_poster)
        background.paste(banner_hdr10, (0, 0), banner_hdr10)
        background.save(tmp_poster)
    def atmos_poster(tmp_poster):
        logger.debug(i.title+' Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(atmos, (0, 0), atmos)
        background.save(tmp_poster)   
    def dtsx_poster(tmp_poster):
        logger.debug(i.title+' Atmos Banner')
        background = Image.open(tmp_poster)
        background.paste(dtsx, (0, 0), dtsx)
        background.save(tmp_poster)  
    def add_banner(tmp_poster):
        background = Image.open(tmp_poster)
        if config[0][14] == 1:
            logger.debug(i.title+' Adding Mini 4K Banner')
            background.paste(mini_4k_banner, (0,0), mini_4k_banner)
        else:
            logger.debug(i.title+' Adding 4k Banner')
            background.paste(banner_4k, (0, 0), banner_4k)
        background.save(tmp_poster)

    def check_banners(tmp_poster):
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

    def scan_files():
        logger.debug('Scanning '+i.title)
        file = re.sub(config[0][5], '/films', i.media[0].parts[0].file)
        m = MediaInfo.parse(file, output='JSON')
        x = json.loads(m)
        hdr_version = ""
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

    def restore_from_tmdb():
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

        def get_poster(poster_url):
            r = requests.get(poster_url_base+poster_url, stream=True)
            if r.status_code == 200:
                r.raw.decode_content = True
                with open('/tmp/poster.png', 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        try:
            poster_url = tmdb_search.poster_path
            tmp_poster = get_poster(poster_url)
            return tmp_poster
        except TypeError:
            logger.warning("RESTORE: "+i.title+" This poster could not be found on TheMoviedb")

    def decision_tree(tmp_poster):
        banners = check_banners(tmp_poster)
        wide_banner = banners[0]
        mini_banner = banners[1]
        audio_banner = banners[2]
        hdr_banner = banners[3]
        old_hdr = banners[4]

        logger.debug(banners)


        resolution = i.media[0].videoResolution
        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            path = config[0][38]
            newdir = os.path.dirname(re.sub(config[0][5], path, i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        if old_hdr == True and config[0][28] == 1:
            if backup == True:
                tmp_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
            elif backup == False and config[0][26] == 1:
                tmp_poster = restore_from_tmdb()
        if (
        audio_banner == False 
        and config[0][35] == 1
        ) or (
        hdr_banner == False
        and config[0][15] ==1
        ):
            scanned = scan_files()
            audio = scanned[0]
            hdr_version = str.lower(scanned[1])
            if audio_banner == False:
                if 'Atmos' in audio and config[0][35] == 1:
                    atmos_poster(tmp_poster)
                elif audio == 'DTS:X' and config[0][35] == 1:
                    dtsx_poster(tmp_poster)

            elif 'Atmos' in audio:
                i.addLabel('Dolby Atmos', locked=False)
            elif audio == 'DTS:X':
                i.addLabel('DTS:X', locked=False)
            if hdr_banner == False:
                if 'dolby vision' in hdr_version and config[0][28] == 1:
                    dolby_vision(tmp_poster)
                elif "hdr10+" in hdr_version and config[0][28] == 1:
                    hdr10(tmp_poster)
                elif hdr_version != "" and config[0][28] == 1:
                    hdr(tmp_poster)
            elif 'dolby vision' in hdr_version:
                i.addLabel('Dolby Vision', locked=False)
            elif 'hdr10+' in hdr_version:
                i.addLabel('HDR10+', locked=False)
            elif hdr_version != '':
                i.addLabel('HDR', locked=False)
        if resolution == '4k' and config[0][24] == 1:
            if wide_banner == mini_banner == False:
                add_banner(tmp_poster)
            else:
                logger.debug(i.title+' Has banner')

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
                logger.warning("4k Posters: "+films.title+ 'cannot find the poster for this film')
        except OSError as e:
            logger.error(e)

    def backup_poster(tmp_poster):
        logger.debug(i.title+' Creating backup')
        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
        shutil.copyfile(tmp_poster, newdir+'poster_bak.png')

    def check_for_new_poster(tmp_poster):
        logger.debug(i.title+' Checking for new poster')
        if config[0][37] == 1:
            newdir = os.path.dirname(re.sub(config[0][38], '/films', i.media[0].parts[0].file))+'/'
        else:
            path = config[0][38]
            newdir = os.path.dirname(re.sub(config[0][5], path, i.media[0].parts[0].file))+'/'
        backup = os.path.exists(newdir+'poster_bak.png')
        if backup == True:
            try:
                bak_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
                bak_poster_hash = imagehash.average_hash(bak_poster)
                poster = Image.open(tmp_poster)
                poster_hash = imagehash.average_hash(poster)
            except SyntaxError:
                logger.warning(i.title+' poster broken, restoring from TMDB')
                restore_from_tmdb()
            except OSError as e:
                logger.debug(i.title)
                logger.warning(repr(e))
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                bak_poster = Image.open(os.path.join(newdir, 'poster_bak.png'))
                bak_poster_hash = imagehash.average_hash(bak_poster)
                poster = Image.open(tmp_poster)
                poster_hash = imagehash.average_hash(poster)
                ImageFile.LOAD_TRUNCATED_IMAGES = False
            
            if poster_hash - bak_poster_hash > cutoff:
                logger.debug(i.title+' - Poster has changed')
                os.remove(os.path.join(newdir, 'poster_bak.png'))
        elif backup == False and config[0][12] == 1:
            try:
                backup_poster(tmp_poster)
            except PermissionError as e:
                logger.error(repr(e))
                   
    def search_lib():
        logger.info('Starting 4K Poster script')
        for i in films.search():
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
            logger.info(i.title)
            t = re.sub(r'[\\/*?:"<>| ]', '_', i.title)
            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
            tmp_poster = get_poster()
            check_for_new_poster(tmp_poster)
            decision_tree(tmp_poster)

            if os.path.exists(tmp_poster) == True:
                try:
                    i.uploadPoster(filepath=tmp_poster)
                except ReadTimeout as e:
                    logger.error(repr(e))
                try:
                    os.remove(tmp_poster)
                except FileNotFoundError:
                    pass 
        logger.info('4k Poster script has finished')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    if config[0][13] == 1:
                        search_lib()
        except IndexError:
            pass          
    else:
        logger.info('4k Posters script is disabled in the config.')

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

    def search_lib():
        if config[0][23] == 1 and config[0][22] != 'None':

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
    lib = config[0][22].split(',')
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    tv = plex.library.section(lib[l])
                    search_lib()
        except IndexError:
            pass  
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
    c.close()

def restore_posters():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]

    plex = PlexServer(config[0][1], config[0][2])
    lib = config[0][3].split(',')

        
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
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
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
    
    def search_lib():
        for i in films.search():
            i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
            newdir = os.path.dirname(re.sub(config[0][5], '/films', i.media[0].parts[0].file))+'/'
            backup = os.path.join(newdir+'poster_bak.png')            
            try:
                os.remove(backup)
            except PermissionError as e:
                logger.error(e)
            except FileNotFoundError as e:
                logger.error(e)
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    search_lib()
        except IndexError:
            pass   
    c.close() 
    logger.info('Restore Completed.')

def hide4k():
    conn = sqlite3.connect('/config/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    tmdb.api_key = config[0][25]
    plex = PlexServer(config[0][1], config[0][2])
    lib = config[0][3].split(',')


    def search_lib():
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
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    search_lib()
        except IndexError:
            pass
    else:
        films = plex.library.section(config[0][3])
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
    lib = config[0][3].split(',')
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
    def search_lib():
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
    
    if len(lib) <= 2:
        try:
            while True:
                for l in range(10):
                    films = plex.library.section(lib[l])
                    search_lib()
        except IndexError:
            pass
    else:
        films = plex.library.section(config[0][3])
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
        i.title = unicodedata.normalize('NFD', i.title).encode('ascii', 'ignore').decode('utf8')
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

def test_script():
    logger.info('test script running')

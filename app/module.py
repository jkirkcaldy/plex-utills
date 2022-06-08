from PIL import Image, ImageFile, ImageFilter
from plexapi.server import PlexServer
import plexapi
import requests
import shutil
import os
import re
import imagehash
import logging
from logging.handlers import RotatingFileHandler
from tmdbv3api import TMDb, Search, Movie, Discover, TV, Episode
from pymediainfo import MediaInfo
import json
from tautulli import RawAPI
import unicodedata
#from flask_sqlalchemy import sqlalchemy

import cv2
import random
import string
from app.scripts import logger


tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
search = Search()
movie = Movie()
discover = Discover()
tmdbtv = Episode()

 

banner_4k = cv2.imread("app/img/4K-Template.png", cv2.IMREAD_UNCHANGED)
banner_4k = Image.fromarray(banner_4k)
mini_4k_banner = cv2.imread("app/img/4K-mini-Template.png", cv2.IMREAD_UNCHANGED)
mini_4k_banner = Image.fromarray(mini_4k_banner)
banner_dv = cv2.imread("app/img/dolby_vision.png", cv2.IMREAD_UNCHANGED)
banner_dv = Image.fromarray(banner_dv)
banner_hdr10 = cv2.imread("app/img/hdr10.png", cv2.IMREAD_UNCHANGED)
banner_hdr10 = cv2.cvtColor(banner_hdr10, cv2.COLOR_BGR2RGBA)
banner_hdr10 = Image.fromarray(banner_hdr10)

banner_new_hdr = cv2.imread("app/img/hdr.png", cv2.IMREAD_UNCHANGED)
banner_new_hdr = Image.fromarray(banner_new_hdr)
atmos = cv2.imread("app/img/atmos.png", cv2.IMREAD_UNCHANGED)
atmos = Image.fromarray(atmos)
dtsx = cv2.imread("app/img/dtsx.png", cv2.IMREAD_UNCHANGED)
dtsx = Image.fromarray(dtsx)
size = (2000,3000)
bannerbox= (0,0,2000,246)
mini_box = (0,0,350,275)
hdr_box = (0,1342,493,1608)
a_box = (0,1608,493,1766)
cutoff = 10


def get_tmdb_guid(g):
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

def get_tmdb_poster(fname, poster):
    req = requests.get(poster_url_base+poster, stream=True)
    if req.status_code == 200:
        #req.raw.decode_content = True
        b_file = '/config/backup/films/'+fname+'.png'
        with open(b_file, 'wb') as f:
            shutil.copyfileobj(req.raw, f)
        return b_file

def check_banners(tmp_poster, size):
    #size = (2000,3000)
    try:
        background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        background = Image.fromarray(background)
        background = background.resize(size,Image.LANCZOS)
    except OSError as e:
        logger.error('Cannot open image: '+repr(e))
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
    if poster_banner_hash - chk_banner_hash <= 10:
        wide_banner = True
    if poster_mini_hash - chk_mini_banner_hash <= 10:
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
    #background.save(tmp_poster)
    return wide_banner, mini_banner, audio_banner, hdr_banner, old_hdr

def get_poster(i, tmp_poster, title):
    logger.debug(i.title+' Getting poster')
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = tmp_poster
    try:
        if img.status_code == 200:
            ##img.raw.decode_content = True
            with open(filename, 'wb') as f:                        
                shutil.copyfileobj(img.raw, f)
            return tmp_poster 
        else:
            logger.info("4k Posters: "+title+ 'cannot find the poster for this film')
    except OSError as e:
        logger.error('Get Poster OSError: '+repr(e))
    except Exception as e:
        logger.error('Get Poster Exception: '+repr(e))

def get_plex_hdr(i, plex):
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

def upload_poster(tmp_poster, title, db, r, table, i):
    try:
        if os.path.exists(tmp_poster) == True:
            logger.debug('uploading poster')
            i.uploadPoster(filepath=tmp_poster) 
            try:
                row = r[0].id
                film = table.query.get(row)
                film.checked = '1'
                db.session.commit()     
            except IndexError as e:
                logger.debug('Updating database to checked: '+repr(e))              
            try:
                os.remove(tmp_poster)
            except FileNotFoundError:
                pass   
        else:
            logger.error('Poster for '+title+" isn't here")
            row = r[0].id
            film = table.query.get(row)
            film.checked = '0'
            db.session.commit()
    except Exception as e:
        logger.error("Can't upload the poster: "+repr(e))         

def scan_files(config, i, plex):
    logger.debug('Scanning '+i.title)
    if config[0].plexpath == '/':
        file = '/films'+i.media[0].parts[0].file
    else:
        file = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
    m = MediaInfo.parse(file, output='JSON')
    x = json.loads(m)
    hdr_version = get_plex_hdr(i, plex)
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
                    try:
                        hdr_version = x['media']['track'][1]['HDR_Format_Compatibillity']
                    except:
                        pass
    audio = "unknown"
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

def backup_poster(tmp_poster, banners, config, r, i, b_dir, g):
    logger.debug("BACKUP")
    logger.debug(banners)
    fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
    if config[0].manualplexpath == 1:
        newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
    else:
        newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
    try:
        old_backup = os.path.exists(newdir+'poster_bak.png')
        if old_backup == True:
            b_file = b_dir+fname+'.png'
            shutil.copy(newdir+'poster_bak.png', b_file)
            return b_file
    except:
        pass
    if True not in banners:
        logger.debug("Poster doesn't have any banners")
        logger.debug(i.title+" No banners detected so adding backup file to database")
        try:
            if r[0].poster:
                b_file = r[0].poster
            else:
                b_file = b_dir+fname+'.png'
        except:
            b_file = b_dir+fname+'.png'
        try:
            b_file = re.sub('static', '/config', b_file)
        except:
            print("this didn't work")
        try:
            shutil.copy(tmp_poster, b_file)
        except:
            pass
        return b_file
    elif True in banners:
        logger.debug('Poster has Banners')
        if r:
                logger.debug("File is in database")
                p = os.path.exists(re.sub('static', '/config', r[0].poster))
                logger.debug(p)
                if p == True:
                    logger.debug("poster found")
                    if 'poster_not_found' not in r[0].poster:
                        b_file = r[0].poster
                        return b_file
                else: #  p == 'False':
                    logger.debug("restoring from tmbd")
                    g = get_tmdb_guid(g)
                    if 'films' in b_dir:
                        tmdb_search = movie.details(movie_id=g)
                        poster = tmdb_search.poster_path
                    elif 'tv' in b_dir:
                        season = str(i.parentIndex)
                        episode = str(i.index)
                        tmdb_search = tmdbtv.details(tv_id=g, episode_num=episode, season_num=season)
                        poster = tmdb_search.still_path
                    logger.info(i.title)
                    b_file = get_tmdb_poster(fname, poster)
                    b_file = re.sub('static', '/config', b_file)
                    return b_file                        
        else:
            logger.debug('not in database')
            if config[0].tmdb_restore == 1:
                try:
                    logger.info('Poster has banners, creating a backup from TheMovieDB')
                    g = get_tmdb_guid(str(i.guids))
                    tmdb_search = movie.details(movie_id=g)
                    logger.info(i.title)
                    poster = tmdb_search.poster_path
                    b_file = get_tmdb_poster(fname, poster)
                    b_file = re.sub('static', '/config', b_file)
                    return b_file
                except Exception as e:
                    logger.error(repr(e))
                    b_file = 'static/img/poster_not_found.png'
                    return b_file
            else:
                logger.warning("This didn't work")


def insert_intoTable(guid, guids, size, res, hdr, audio, tmp_poster, banners, title, config, table, db, r, i, b_dir, g, blurred):
    if config[0].manualplexpath == 1:
        newdir = os.path.dirname(re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file))+'/'
    else:
        newdir = os.path.dirname(re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')            
    logger.debug(title+' '+hdr+' '+audio)
    if blurred == False:  
        b_file = backup_poster(tmp_poster, banners, config, r, i, b_dir, g)
    else:
        title = re.sub(r'[\\/*?:"<>| ]', '_', title)
        tmp_poster = re.sub(' ','_', '/tmp/'+title+'_poster.png')
        tmp_poster = get_poster(i, tmp_poster, title)
    if 'config' in b_file:
        b_file = re.sub('/config', 'static', b_file)
    logger.debug('Adding '+i.title+' to database')
    film = table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file, checked='1')
    db.session.add(film)
    db.session.commit()

def updateTable(guid, guids, size, res, hdr, audio, tmp_poster, banners, title, config, table, db, r, i, b_dir, g, blurred):
    logger.debug('Updating '+title+' in database')
    logger.debug(title+' '+hdr+' '+audio)  
    logger.debug(banners) 
    if blurred == False:
        b_file = backup_poster(tmp_poster, banners, config, r, i, b_dir, g)
        logger.debug(b_file)
        if 'config' in b_file:
            b_file = re.sub('/config', 'static', b_file)
    else:
        b_file = r[0].poster
    
    logger.debug('Updating '+title+' in database')
    row = r[0].id
    film = table.query.get(row)
    film.size = size
    film.res = res
    film.hdr = hdr
    film.audio = audio
    film.poster = b_file
    film.checked = '1'
    db.session.commit()

def blur(tmp_poster, r, table, db):
    poster = re.sub('.png', '.blurred.png', tmp_poster)
    background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    background = Image.fromarray(background)
    blur = background.filter(ImageFilter.GaussianBlur(30))
    blur.save(poster)
    row = r[0].id
    film = table.query.get(row)
    film.blurred = '1'
    db.session.commit()
    return poster

def check_tv_banners(tmp_poster, img_title):
    size = (1280,720)
    logger.debug(tmp_poster)
    size = (1280,720)
    box_4k= (42,45,290,245)
    hdr_box = (32,440,303,559)
    a_box = (32,560,306,685)
    cutoff = 10
    logger.debug(img_title+' Checking for Banners')
    try:
        size = (1280,720)
        background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)#Image.open(tmp_poster)
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        background = Image.fromarray(background)
        background = background.resize(size,Image.LANCZOS)
    except OSError as e:
        logger.error(e)

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



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
from pathlib import PureWindowsPath, PurePosixPath
import cv2
import random
import string
import time

tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
search = Search()
movie = Movie()
discover = Discover()
tmdbtv = Episode()
from app.scripts import logger
 

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
    
def tmdb_poster_path(b_dir, i, g, episode, season):
    if 'film' in b_dir:
        logger.debug("is a film")
        tmdb_search = movie.details(movie_id=g)
        poster2_search = movie.images(movie_id=g)
        logger.debug(poster2_search)
        logger.info(i.title)
        poster = tmdb_search.poster_path
        return poster
    elif 'episodes' in b_dir:
        logger.debug("is TV")
        logger.debug(g+':'+season+'_'+episode)
        tmdb_search = tmdbtv.details(tv_id=g, episode_num=episode, season_num=season)
        poster = tmdb_search.still_path 
        return poster

def get_tmdb_poster(fname, poster):
    req = requests.get(poster_url_base+poster, stream=True)
    logger.debug("tmdb: "+poster_url_base+poster)
    logger.debug(fname)
    if req.status_code == 200:
        b_file = '/config/backup/films/'+fname+'.png'
        with open(fname, 'wb') as f:
            for chunk in req:
                f.write(chunk)
        return fname
    else:
        logger.error("Can't get poster from TMDB")

def check_banners(tmp_poster, size):
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

def get_poster(i, tmp_poster, title, b_dir):
    logger.debug(i.title+' Getting poster')
    imgurl = i.posterUrl
    logger.debug(i.posterUrl)
    img = requests.get(imgurl, stream=True)
    filename = tmp_poster
    print(tmp_poster)
    try:
        if img.status_code == 200:
            img.raw.decode_content = True
            with open(filename, 'wb') as f:                        
                for chunk in img:
                    f.write(chunk)
        else:
            logger.info("4k Posters: "+title+ 'cannot find the poster for this film')
    except OSError as e:
        logger.error('Get Poster OSError: '+repr(e))
    except Exception as e:
        logger.error('Get Poster Exception: '+repr(e))

    valid = validate_image(tmp_poster)
    if valid == True:
        return tmp_poster
    else:
        logger.warning("poster is blank, getting poster from TMDB")
        t = re.sub('plex://movie/', '', i.guid)
        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
        g = str(i.guids)
        g = get_tmdb_guid(g)
        poster = tmdb_poster_path(b_dir, i, g, '', '')
        tmp_poster = get_tmdb_poster(tmp_poster, poster)
        return tmp_poster
    
def get_season_poster(ep, tmp_poster, title, config):
        logger.debug(ep.title+' Getting poster')
        title = ep.title
        imgurl = config[0].plexurl+ep.parentThumb
        logger.debug(imgurl)
        img = requests.get(imgurl, stream=True)
        filename = tmp_poster
        try:
            if img.status_code == 200:
                img.raw.decode_content = True
                with open(filename, 'wb') as f:                        
                    for chunk in img:
                        f.write(chunk)
                return tmp_poster 
            else:
                logger.info("Get Poster: "+title+ ' - cannot find the poster for this film')
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
                try:
                    i.addLabel('Dolby Vision', locked=False)
                except:
                    pass
                if m.media[0].parts[0].streams[0].DOVIProfile == 5:
                    logger.error(i.title+" is version 5")
            elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                hdr_version='HDR'
                try:
                    i.addLabel('HDR', locked=False)
                except:
                    pass
            else:
                hdr_version = 'none'
            return hdr_version
        except IndexError:
            pass

def validate_image(tmp_poster):
    try:
        img = Image.open(tmp_poster)
        img.verify()
        logger.debug("Image is valid")
        valid = True
        return valid
    except Exception as e:
        logger.error(repr(e))
        logger.debug("Image is invalid")
        valid = False
        return valid

def upload_poster(tmp_poster, title, db, r, table, i):
    db.session.close() 
    try:
        if os.path.exists(tmp_poster) == True:
            try:
                valid = validate_image(tmp_poster)
                if valid == True:
                    logger.debug('uploading poster')
                    i.uploadPoster(filepath=tmp_poster)
                    time.sleep(2)
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
            except (IOError, SyntaxError) as e:
              logger.error('Bad file: '+title)                 
        else:
            logger.error('Poster for '+title+" isn't here")
            row = r[0].id
            film = table.query.get(row)
            film.checked = '0'
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise logger.error(Exception('Database Roll back error'))
            finally:
                db.session.close()
    except Exception as e:
        logger.error("Can't upload the poster: "+repr(e))         

def scan_files(config, i, plex):
    logger.debug('Scanning '+i.title)
    p = PureWindowsPath(i.media[0].parts[0].file)
    p1 = re.findall('[A-Z]', p.parts[0])
    if p1 != []:
        logger.debug('path is: '+str(p1))
        file = PurePosixPath('/films', *p.parts[1:])
    elif config[0].manualplexpath == 1:
        file = re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file)
    else:
        file = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
    logger.debug(file)
    m = MediaInfo.parse(file, output='JSON')
    x = json.loads(m)
    hdr_version = get_plex_hdr(i, plex)
    if hdr_version != 'none':
        try:
            hdr_version = x['media']['track'][1]['HDR_Format_String']
        except (KeyError, IndexError):
            if "dolby" not in str.lower(hdr_version):
                try:
                    hdr_version = x['media']['track'][1]['HDR_Format_Commercial']
                except (KeyError, IndexError):
                    try:
                        hdr_version = x['media']['track'][1]    ['HDR_Format_Commercial_IfAny']
                    except (KeyError, IndexError):
                        try:
                            hdr_version = x['media']['track'][1]    ['HDR_Format_Compatibillity']
                        except:
                            pass
    elif not hdr_version:
        hdr_version = 'none'
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

def backup_poster(tmp_poster, banners, config, r, i, b_dir, g, episode, season, guid):
    logger.debug("BACKUP")
    logger.debug(banners)
    if episode !='':
        fname = t = re.sub('plex://episode/', '', guid)
    else:
        fname = re.sub('plex://movie/', '', guid)
    #fname = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))
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
                    g = get_tmdb_guid(str(g))

                    poster = tmdb_poster_path(b_dir, i, g, episode, season)
                    b_file = get_tmdb_poster(fname, poster)
                    b_file = re.sub('static', '/config', b_file)
                    return b_file
                except Exception as e:
                    logger.error(repr(e))
                    b_file = 'static/img/poster_not_found.png'
                    return b_file
            else:
                logger.warning("This didn't work")

def insert_intoTable(guid, guids, size, res, hdr, audio, tmp_poster, banners, title, config, table, db, r, i, b_dir, g, blurred, episode, season):
    db.session.close()
    p = PureWindowsPath(i.media[0].parts[0].file)
    p1 = re.findall('[A-Z]', p.parts[0])    
    if p1 != []:
        newdir = PurePosixPath('/films', *p.parts[1:])
    elif config[0].manualplexpath == 1:
        newdir = re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file)
    else:
        newdir = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)           
    logger.debug(title+' '+hdr+' '+audio)
    if blurred == False:  
        b_file = backup_poster(tmp_poster, banners, config, r, i, b_dir, g, episode, season, guid)
    else:
        title = re.sub(r'[\\/*?:"<>| ]', '_', title)
        tmp_poster = re.sub(' ','_', '/tmp/'+title+'_poster.png')
        tmp_poster = get_poster(i, tmp_poster, title)
    try:
        if 'config' in b_file:
            b_file = re.sub('/config', 'static', b_file)
    except:
        pass
    logger.debug('Adding '+i.title+' to database')
    film = table(title=title, guid=guid, guids=guids, size=size, res=res, hdr=hdr, audio=audio, poster=b_file, checked='1')
    try:
        db.session.add(film)
        db.session.commit()
    except:
        db.session.rollback()
        raise logger.error(Exception('Database Roll back error'))
    finally:
        db.session.close()

def updateTable(guid, guids, size, res, hdr, audio, tmp_poster, banners, title, config, table, db, r, i, b_dir, g, blurred, episode, season):
    db.session.close()
    logger.debug('Updating '+title+' in database')
    logger.debug(title+' '+hdr+' '+audio)  
    logger.debug(banners) 
    if blurred == False:
        b_file = backup_poster(tmp_poster, banners, config, r, i, b_dir, g, episode, season, guid)
        logger.debug(b_file)
        if 'config' in b_file:
            b_file = re.sub('/config', 'static', b_file)
    else:
        b_file = r[0].poster
    try:
        logger.debug('Updating '+title+' in database')
        row = r[0].id
        film = table.query.get(row)
        film.size = size
        film.res = res
        film.hdr = hdr
        film.audio = audio
        film.poster = b_file
        film.checked = '0'
        db.session.commit()
    except:
        db.session.rollback()
        raise logger.error(Exception('Database Roll back error'))
        
    finally:
        db.session.close()

def blur(tmp_poster, r, table, db, guid):
    poster = re.sub('.png', '.blurred.png', tmp_poster)
    background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    background = Image.fromarray(background)
    blur = background.filter(ImageFilter.GaussianBlur(30))
    blur.save(poster)
    from app.models import ep_table
    r = ep_table.query.filter(ep_table.guid == guid).all()
    row = r[0].id
    film = table.query.get(row)
    film.blurred = '1'
    db.session.commit()
    return poster

def check_tv_banners(i, tmp_poster, img_title):
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
        background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        background = Image.fromarray(background)
        background = background.resize(size,Image.LANCZOS)
    except OSError as e:
        logger.error(e)
        try:    
            title = img_title
            get_poster(i, tmp_poster, title)
            size = (1280,720)
            background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
            background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            background = Image.fromarray(background)
            background = background.resize(size,Image.LANCZOS)
        except Exception as e:
            logger.critical("Check TV Banners: "+repr(e))

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
    #background.save(tmp_poster)
    return banner_4k, audio_banner, hdr_banner

def add_bannered_poster_to_db(tmp_poster, db, title, table, guid, banner_file):
    logger.debug(banner_file)
    shutil.copy(tmp_poster, banner_file)
    try:    
        logger.debug('Updating '+title+' in database')
        r = table.query.filter(table.guid == guid).all()
        row = r[0].id
        media = table.query.get(row)       
        media.bannered_poster = re.sub('/config', 'static', banner_file)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(repr(e))
        
    finally:
        db.session.close()

def check_for_new_poster(tmp_poster, r, i):
    new_poster = 'False'
    if r:
        try:
            poster_file = r[0].poster
            poster_file = re.sub('static', '/config', poster_file)
            logger.debug(poster_file)
            try:
                bak_poster = cv2.imread(poster_file, cv2.IMREAD_ANYCOLOR)
                bak_poster = cv2.cvtColor(bak_poster, cv2.COLOR_BGR2RGB)
                bak_poster = Image.fromarray(bak_poster)
                bak_poster_hash = imagehash.average_hash(bak_poster)
                poster = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)
                poster = cv2.cvtColor(poster, cv2.COLOR_BGR2RGB)
                poster = Image.fromarray(poster)
                poster_hash = imagehash.average_hash(poster)
            except SyntaxError as e:
                    logger.error('Check for new poster Syntax Error: '+repr(e))
            except OSError as e:
                    logger.error('Check for new poster OSError: '+repr(e))
                    if 'FileNotFoundError'  or 'Errno 2 'in e:
                        logger.debug(i.title+' - Poster Not found')
                        new_poster = 'True'
                        return new_poster
                    else:
                        logger.debug(i.title)
                        logger.warning('Check for new Poster: '+repr(e))

            if poster_hash - bak_poster_hash > cutoff:
                logger.debug(i.title+' - Poster has changed')
                new_poster = 'True'
                return new_poster                      
            else:
                logger.debug('Poster has not changed')
                return new_poster       
        except Exception as e:
            logger.error('Check for new poster Exception: '+repr(e))
            if '!_src.empty()' in str(e):
                logger.error("poster is blank")
                new_poster = 'BLANK'
            else:
                logger.debug('Film not in database yet')
                new_poster = 'True'
            return new_poster
    else:
        new_poster='True'
        return new_poster

def season_decision_tree(config, banners, ep, hdr, res, tmp_poster):
    wide_banner = banners[0]
    mini_banner = banners[1]
    hdr_banner = banners[3]

    logger.debug(banners)
    logger.debug("Decision tree")    

    if (hdr != 'none' and config[0].hdr == 1 and hdr_banner == False):
        logger.info(ep.title+" HDR Banner")
        try:
            size = (2000,3000)
            background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)#Image.open(tmp_poster)
            background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            background = Image.fromarray(background)
            background = background.resize(size,Image.LANCZOS)
            background.paste(banner_new_hdr, (0, 0), banner_new_hdr)
            background.save(tmp_poster)
        except OSError as e:
            logger.error('HDR Poster error: '+repr(e))
    else:
        logger.debug("Not adding hdr season banner")
    if (res == '4k' and config[0].films4kposters == 1 and wide_banner == mini_banner == False):
        try:
            size = (2000,3000)
            background = cv2.imread(tmp_poster, cv2.IMREAD_ANYCOLOR)#Image.open(tmp_poster)
            background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
            background = Image.fromarray(background)
            background = background.resize(size,Image.LANCZOS)
            if config[0].mini4k == 1:
                logger.info(ep.title+' Adding Mini 4K Banner')
                background.paste(mini_4k_banner, (0,0), mini_4k_banner)
                background.save(tmp_poster)
            else:
                logger.info(ep.title+' Adding 4k Banner')
                background.paste(banner_4k, (0, 0), banner_4k)
                background.save(tmp_poster)
        except OSError as e:
            logger.error('4K poster error: '+repr(e))
    else:
        logger.debug("Not adding 4k season banner")            

def remove_tmp_files(tmp_poster):
    try:
        os.remove(tmp_poster)
    except FileNotFoundError:
        pass  
    

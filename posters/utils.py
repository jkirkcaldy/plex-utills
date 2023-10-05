import cv2, imagehash
import requests
import re
from PIL import Image
from pathlib import PureWindowsPath, PurePosixPath
from pymediainfo import MediaInfo
import json
from plexapi.server import PlexServer
from plexapi.exceptions import BadRequest
from django.conf import settings
import os
from datetime import datetime
from tzlocal import get_localzone # $ pip install tzlocal
from django.core.files.storage import default_storage
from tmdbv3api import TMDb, Search, Movie, Discover, TV, Episode, Season
import logging
from utils.models import Plex, advancedSettings
from django.shortcuts import get_object_or_404
import shutil

tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
search = Search()
movie = Movie()
discover = Discover()
tmdbtv = Episode()
tmdbSeason = Season()
tmdbShow = TV()


logger = logging.getLogger(__name__)
class banners:
    def bannerTemplate(bannerType):
        if bannerType == 'banner_4k':
            Type = "static/banners/4K-Template.png"
        elif bannerType == 'mini_4k':
            Type = "static/banners/4K-mini-Template.png"
        elif bannerType == 'banner_3d':
            Type = "static/banners/3D-Template.png"
        elif bannerType == 'mini_3d':
            Type = "static/banners/3D-mini-Template.png"            
        elif bannerType == 'hdr10':
            Type = "static/banners/hdr10.png"
        elif bannerType == 'hdr':
            Type = "static/banners/hdr.png"
        elif bannerType == 'dv':
            Type = "static/banners/dolby_vision.png"
        elif bannerType == 'atmos':
            Type = "static/banners/atmos.png"
        elif bannerType == 'dtsx':
            Type = "static/banners/dtsx.png"
        banner = Image.open(Type)
        return banner
    
    def episodeBannerTemplate(bannerType):
        if bannerType == 'banner_4k':
            Type = "static/banners/tv/4k.png"
        elif bannerType == 'hdr10':
            Type = "static/banners/tv/hdr10.png"
        elif bannerType == 'hdr':
            Type = "static/banners/tv/hdr.png"
        elif bannerType == 'dv':
            Type = "static/banners/tv/dolby_vision.png"
        elif bannerType == 'atmos':
            Type = "static/banners/tv/atmos.png"
        elif bannerType == 'dtsx':
            Type = "static/banners/tv/dtsx.png"
        banner = Image.open(Type)
        return banner
    
    def episodeBannerBackground(poster, size):
        banner_bg = Image.open("static/banners/tv/Background.png")
        processedPoster = Image.open(poster) #Image.fromarray(cv2.imread(poster, cv2.COLOR_BGR2RGBA))
        processedPoster.resize(size, Image.LANCZOS)
        processedPoster.paste(banner_bg, (0,0), banner_bg)
        processedPoster.save(poster)
        
    def baseHash(bannerType):
        if bannerType == 'banner_4k':
            hash = "static/banners/chk-4k.png"
        elif bannerType == 'mini_4k':
            hash = "static/banners/chk-mini-4k2.png"
        elif bannerType == 'banner_3d':
            hash = "static/banners/chk_3d_wide.png"
        elif bannerType == 'mini_3d':
            hash = "static/banners/chk-3D-mini.png"            
        elif bannerType == 'hdr10':
            hash = "static/banners/chk_hdr10.png"
        elif bannerType == 'hdr':
            hash = "static/banners/chk_hdr_new.png"
        elif bannerType == 'dv':
            hash = "static/banners/chk_dolby_vision.png"
        elif bannerType == 'atmos':
            hash = "static/banners/chk_atmos.png"
        elif bannerType == 'dtsx':
            hash = "static/banners/chk_dtsx.png"
        baseHash = imagehash.average_hash(Image.open(hash))
        return baseHash
    
    def episodeBaseHash(bannerType):
        if bannerType == 'banner_4k':
            hash = "static/banners/tv/chk_4k.png"
        elif bannerType == 'hdr10':
            hash = "static/banners/tv/chk_hdr10.png"
        elif bannerType == 'hdr':
            hash = "static/banners/tv/chk_hdr.png"
        elif bannerType == 'dv':
            hash = "static/banners/tv/chk_dv.png"
        elif bannerType == 'atmos':
            hash = "static/banners/tv/chk_atmos.png"
        elif bannerType == 'dtsx':
            hash = "static/banners/tv/chk_dts.png"
        episodeBaseHash = imagehash.average_hash(hash)        
        return episodeBaseHash
    
    def posterHash(poster):
        posterHash = imagehash.average_hash(Image.fromarray(cv2.imread(poster, cv2.IMREAD_UNCHANGED)))
        return posterHash
    
    def epPosterHash(poster):
        posterHash = imagehash.average_hash(Image.fromarray(cv2.imread(poster, cv2.IMREAD_UNCHANGED)).resize((1280,720),Image.LANCZOS).crop((640,0,1280,720)))
        return posterHash    

    def posterBannerHash(poster, size):
        bannerbox= (0,0,2000,220)
        mini_box = (0,0,350,275)
        hdr_box = (0,1342,493,1608)
        a_box = (0,1608,493,1766)

        background = cv2.imread(poster, cv2.IMREAD_UNCHANGED)
        background = Image.fromarray(background)
        background = background.resize(size,Image.LANCZOS)

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
        hash = [poster_banner_hash, poster_mini_hash, poster_audio_hash, poster_hdr_hash]
        return hash 
    
    def episodePosterHash(poster, size):
        box_4k= (42,45,290,245)
        hdr_box = (32,440,303,559)
        a_box = (32,560,306,685)

        background = cv2.imread(poster, cv2.IMREAD_UNCHANGED)
        background = Image.fromarray(background)
        background = background.resize(size,Image.LANCZOS)

        # 4K banner box
        bannerchk = background.crop(box_4k)
        # Audio Box
        audiochk = background.crop(a_box)
        # HDR Box
        hdrchk = background.crop(hdr_box)

        poster_banner_hash = imagehash.average_hash(bannerchk)
        # Audio Banner
        poster_audio_hash = imagehash.average_hash(audiochk)
        # HDR Banner
        poster_hdr_hash = imagehash.average_hash(hdrchk)

        return poster_banner_hash, poster_audio_hash, poster_hdr_hash

    def hdrBannerCheck(posterBannerHash):
        if posterBannerHash[3] - banners.baseHash('dv') <= 10:
            dolbyVisionBanner = 'True'
        else: dolbyVisionBanner = False
        if posterBannerHash[3] - banners.baseHash('hdr') <= 10:
            hdrBanner = 'True'
        else: hdrBanner = False
        if posterBannerHash[3] - banners.baseHash('hdr10') <= 10:
            hdr10Banner = 'True' 
        else: hdr10Banner = False    
        return dolbyVisionBanner, hdr10Banner, hdrBanner
    
    def audioBannerCheck(posterBannerHash):
        if posterBannerHash[2] - banners.baseHash('atmos') <= 10:
            atmosBanner = 'True'
        else: atmosBanner = False
        if posterBannerHash[2] - banners.baseHash('dtsx') <= 10:
            dtsxBanner = 'True'    
        else: dtsxBanner = False    
        return atmosBanner, dtsxBanner
    
    def resolutionBannerCheck(posterBannerHash):
        if posterBannerHash[0] - banners.baseHash('banner_4k') <= 10:
            wideBanner = 'True'
        else: wideBanner = False
        if posterBannerHash[1] - banners.baseHash('mini_4k') <= 10:
            mini4kBanner = 'True' 
        else: mini4kBanner = False
        return wideBanner, mini4kBanner       

    def banner3dCheck(posterBannerHash):
        if posterBannerHash[0] - banners.baseHash('banner_3d') <= 10:
            wideBanner = True
        else: wideBanner = False
        if posterBannerHash[1] - banners.baseHash('mini_3d') <= 10:
            mini3dBanner = True
        else: mini3dBanner = False
        return wideBanner, mini3dBanner

class item:
    def getConfig():
        config = Plex.objects.first()
        advancedConfig = advancedSettings.objects.first()
        if not advancedConfig:
            ac = advancedSettings(mountedpath='/films')
            ac.save()
            advancedConfig = advancedSettings.objects.filter(pk='1').first()
        return config, advancedConfig
    
    def getPlex():
        p = Plex.objects.filter(pk='1').first()
        try:
            plex = PlexServer(p.plexurl, p.token)
            return plex
        except:
            logger.error('Plex Server not reachable')
    
    def tmpPoster(self, mediaType):
        #logger.debug('Getting temp poster')
        if mediaType == 'film':
            t = re.sub('plex://movie/', '', self.guid)
        elif mediaType == 'episode':
            t = re.sub('plex://episode/', '', self.guid)
        elif mediaType == 'season':
            t = re.sub('plex://season/', '', self.guid)
        elif mediaType == 'show':
            t = re.sub('plex://show/', '', self.guid)
        if 'local://' in self.guid:
            t = re.sub('local://', '', self.guid)
        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
        #logger.debug(tmp_poster)    
        return tmp_poster, t
    
    def libraries(mediaType):
        libraries = []
        config, advancedConfig = item.getConfig()
        plex = item.getPlex()
        if mediaType == 'film':
            lib = config.filmslibrary.split(',')
        elif mediaType == 'episode': 
            lib = config.tvlibrary.split(',')
        elif mediaType == '3d':
            lib = config.library3d.split(',')
        n = len(lib)
        if n >= 2:
            try:
                for l in range(n):
                    libraries.append(plex.library.section(lib[l].lstrip()))

            except IndexError:
                pass
        else:
            libraries.append(plex.library.section(lib[0]))
        return libraries
    
    def sanitiseFilepath(self):
        #logger.debug('sanitising filepath')
        config, advancedConfig = item.getConfig()
        p = PureWindowsPath(self.media[0].parts[0].file)
        p1 = re.findall('[A-Z]', p.parts[0])
        if p1 != []:
            file = PurePosixPath('/films', *p.parts[1:])
        if advancedConfig.manualplexpath == 1:
            file = re.sub(advancedConfig.manualplexpathfield, advancedConfig.mountedpath, self.media[0].parts[0].file)
        else:
            file = re.sub('/media', advancedConfig.mountedpath, self.media[0].parts[0].file)
        return file        
    
    def getAudio(self, db):
        #logger.debug('Getting Plex audio')
        try:
            try:
                if 'Atmos' in self.media[0].parts[0].streams[1].extendedDisplayTitle:
                    audio = 'Dolby Atmos'

                if (self.media[0].parts[0].streams[1].title and 'DTS:X' in self.media[0].parts[0].streams[1].title):
                    audio = 'DTS:X'
            except: pass
            else:
                audio = self.media[0].parts[0].streams[1].displayTitle
        except: audio = 'unknown'
        #logger.debug(audio)
        #i = db.objects.filter(guid=self.guid).first()
        #i.audio = str.lower(audio)
        #i.save()
        return str.lower(audio)
    
    def getHdr(self, db):
        try:
            plex = item.getPlex()
            ekey = self.key
            m = plex.fetchItems(ekey)
            for m in m:
                try:
                    if m.media[0].parts[0].streams[0].DOVIPresent == True:
                        hdrVersion='dovi'
                    elif 'HDR' in m.media[0].parts[0].streams[0].displayTitle:
                        hdrVersion='hdr'
                    else:
                        hdrVersion = 'None'
                except IndexError:
                    pass
        except AttributeError:
            hdrVersion = 'None'
        return hdrVersion
    
    def poster(self, fileName, size):
        plex = item.getPlex()
        imgurl = plex.transcodeImage(
            self.thumbUrl,
            height=size[1],
            width=size[0],
            imageFormat='png'
        )
        img = requests.get(imgurl, stream=True)
        if img.status_code == 200:
            img.raw.decode_content = True
            with open(fileName, 'wb') as f:
                for chunk in img:
                    f.write(chunk)
        else: logger.error('Error downloading poster')
        return fileName

    def blurposter(self, fileName, size):
        plex = item.getPlex()
        imgurl = plex.transcodeImage(
            self.thumbUrl,
            height=size[1],
            width=size[0],
            imageFormat='png',
            blur=30
        )
        img = requests.get(imgurl, stream=True)
        if img.status_code == 200:
            img.raw.decode_content = True
            with open(fileName, 'wb') as f:
                for chunk in img:
                    f.write(chunk)
        else: logger.error('Error downloading poster')
        return fileName

    def scanFile(self, filePath, db, hdr, audio):
        #logger.debug('scanning file')
        versions = ['dovi', 'hdr', 'hdr10', 'hdr10+']
        try:
            m = MediaInfo.parse(filePath, output='JSON')
            x = json.loads(m)
            if any(h in hdr for h in versions):
                hdrVersion = hdr
            if 'hdr' in hdr:
                try:
                    hdrVersion = x['media']['track'][1]['HDR_Format_Compatibility']
                except: pass
            else: hdrVersion = 'None'
            try:
                for f in range(10):
                    if 'Audio' in x['media']['track'][f]['@type']:
                        if 'XLL X' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                            audio = 'DTS:X'
                            break
                        elif '16-ch' in x['media']['track'][f]["Format_AdditionalFeatures"]:
                            audio = 'Atmos'
                            break
                        else:
                            audio = item.getAudio(self, db)
                            break
            except Exception as e:
                if 'TypeError' in str(e):
                    audio = audio
                    pass
        except FileNotFoundError:
            hdrVersion = hdr
        #logger.debug('Scanned: '+hdrVersion+' '+audio)

        return str.lower(hdrVersion), str.lower(audio)

    def savePoster(self, mediaType, t, poster, db):
        name = f'backup/{mediaType}/backup/{t}.png'
        fpath = os.path.join(settings.MEDIA_ROOT, name)
        path = os.path.dirname(fpath)
        if os.path.exists(path) == False:
            os.makedirs(path)
        if file.file_exists(name) == True:
            logger.debug('removing old backup poster')
            try:
                os.remove(fpath)
            except Exception:
                pass
        shutil.copy(poster, fpath)
        i = db.objects.get(guid=self.guid)
        i.poster= name
        i.save()
    
    def newPoster(self, poster, mediaType, t, db, size):   
        try:
            dbPoster = db.objects.get(guid=self.guid)
            try:
                logger.debug('db poster exists')
                dbPoster = os.path.join(settings.MEDIA_ROOT, dbPoster.poster)
                if mediaType == 'episode':
                    bakPoster = imagehash.average_hash(Image.fromarray(cv2.imread(dbPoster, cv2.IMREAD_UNCHANGED)).resize(size,Image.LANCZOS).crop((640,0,1280,720)))
                else:
                    bakPoster = imagehash.average_hash(Image.fromarray(cv2.imread(dbPoster, cv2.IMREAD_UNCHANGED)).resize(size,Image.LANCZOS))
                posterHash = banners.epPosterHash(poster)
                if posterHash - bakPoster > 10:
                    newPoster = True
                else: 
                    newPoster = False
                    hdrBanners = [False, False, False]
                    audioBanners = [False, False]
                    resBanners = [False, False]
            except Exception as e:
                logger.error('NewPoster: '+repr(e))
                newPoster = True
        except db.DoesNotExist as e:
            logger.error(f'New poster: {repr(e)}')
            newPoster = True
            pass
        logger.info(f'{self.title} new poster: {str(newPoster)}')
        if newPoster == True:
            posterBannerHash = banners.posterBannerHash(poster, size)
            hdrBanners = banners.hdrBannerCheck(posterBannerHash)
            audioBanners = banners.audioBannerCheck(posterBannerHash)
            resBanners = banners.resolutionBannerCheck(posterBannerHash)
            if 'True' not in hdrBanners+ audioBanners+ resBanners:
                logger.debug(f"Saving {self.title}'s poster")
                try:
                    item.savePoster(self, mediaType, t, poster, db)
                except: pass
            else:
                logger.warning(self.title+': will not be backed up in database due to banners appearing on Plex Poster')

        return newPoster, hdrBanners, audioBanners, resBanners
    
    def new3dPoster(self, poster, mediaType, t, db, size):   
        try:
            dbPoster = db.objects.get(guid=self.guid)
            try:
                logger.debug('db poster exists')
                dbPoster = os.path.join(settings.MEDIA_ROOT, dbPoster.poster)
                bakPoster = imagehash.average_hash(Image.fromarray(cv2.imread(dbPoster, cv2.IMREAD_UNCHANGED)).resize(size,Image.LANCZOS).crop((640,0,1280,720)))
                posterHash = banners.posterHash(poster)
                if posterHash - bakPoster > 10:
                    newPoster = True
                else: 
                    newPoster = False
                    banners3d = [False, False]
            except Exception as e:
                logger.error('NewPoster: '+repr(e))
                newPoster = True
        except db.DoesNotExist as e:
            logger.error(f'New poster: {repr(e)}')
            newPoster = True
            pass
        logger.info(f'{self.title} new poster: {str(newPoster)}')
        if newPoster == True:
            posterBannerHash = banners.posterBannerHash(poster, size)
            banners3d = banners.banner3dCheck(posterBannerHash)
            if 'True' not in banners3d:
                logger.debug(f"Saving {self.title}'s poster")
                try:
                    item.savePoster(self, mediaType, t, poster, db)
                except: pass
            else:
                logger.warning(self.title+': will not be backed up in database due to banners appearing on Plex Poster')

        return newPoster, banners3d

    def getShowGuid(self, library, guid):
        for show in library.search(libtype='show', guid=guid):
            #logger.debug(show.guids)
            return str(show.guids)
    
    def getParent(library, guid, mediaType):
        for item in library.search(libtype=mediaType, guid=guid):
            return item      
    
    def file_needs_scan(self):
        scanRequired = False
        if 'TrueHD' in self.audio or 'DTS-HD' in self.audio:
            scanRequired = True
        if 'DoVi' in self.hdr or 'HDR10' in self.hdr:
            scanRequired = True
        if self.resolution == '4k':
            scanRequired = True
        return scanRequired


class process:
    def addBanner(self, t, bannerType, poster, size, mediaType, db):
        processedPoster = Image.open(poster) 
        processedPoster.resize(size, Image.LANCZOS)
        if mediaType != 'episode':
            banner = banners.bannerTemplate(bannerType)
        else:
            banner = banners.episodeBannerTemplate(bannerType)
        processedPoster.paste(banner, (0,0), banner)
        processedPoster.save(poster)
        name = f'backup/{mediaType}/bannered/{t}_bannered.png'
        fname = os.path.join(settings.MEDIA_ROOT, name)
        path = os.path.dirname(os.path.join('/config', name))
        if os.path.exists(path) == False:
            os.makedirs(path)
        try:
            if file.file_exists(name) == True:
               os.remove(fname)
        except FileNotFoundError as e:
            logger.warning(f"Add banners Error: {repr(e)}")
            pass
        shutil.copy(poster, fname)
        logger.debug('saving bannered :'+name)
        dbPoster = db.objects.get(guid=self.guid)
        dbPoster.bannered_poster = name
        dbPoster.checked = True
        dbPoster.save()

    def bannerDecisions(self, res, resBanners ,hdr, hdrBanners, audio, audioBanners, t, poster, size, mediaType, db):
        if mediaType == 'season' or mediaType == 'show':
            if hdr == True:
                logger.info('adding hdr banner')
                process.addBanner(self, t, 'hdr', poster, size, mediaType, db) 
        else:
            if 'dovi' in hdr or 'hdr' in hdr:
                dolbyVisionBanner = hdrBanners[0]
                hdr10Banner = hdrBanners[1]
                hdrBanner = hdrBanners[2]
                logger.debug(f'Banner Decision, HDR updating database')
                process.dbUpdate(self, db, hdr, audio, mediaType)
                if hdr == 'dovi' and dolbyVisionBanner == False:
                    logger.info('adding DoVi banner')
                    process.addBanner(self, t, 'dv', poster, size, mediaType, db) 
                elif 'hdr10+' in hdr and hdr10Banner == False:
                    logger.info('adding hdr10+ banner')
                    process.addBanner(self, t, 'hdr10', poster, size, mediaType, db)
                elif 'hdr' in hdr and '+' not in hdr and hdrBanner == False:
                    logger.info('adding hdr banner')
                    process.addBanner(self, t, 'hdr', poster, size, mediaType, db) 
            else: logger.info(self.title+': does not need hdr banner')
            if ('atmos' in audio or 'dts:x' in audio):
                atmosBanner = audioBanners[0]
                dtsxBanner = audioBanners[1]
                logger.debug(f'Banner Decision, Audio updating database')
                process.dbUpdate(self, db, hdr, audio, mediaType)
                if audio == 'atmos' and atmosBanner == False:
                    logger.info('adding Atmos banner')
                    process.addBanner(self, t, 'atmos', poster, size, mediaType, db)
                if audio == 'dts:x' and dtsxBanner == False:
                    logger.info('adding DTS:X banner')
                    process.addBanner(self, t, 'dtsx', poster, size, mediaType, db)
            else: logger.info(self.title+': does not need audio banner')
        if res == '4k':
            wideBanner = resBanners[0]
            mini4kBanner = resBanners[1]
            logger.debug(f'Banner Decision, RES updating database')
            process.dbUpdate(self, db, hdr, audio, mediaType)
            logger.info('adding 4K banner')
            config, advancedConfig = item.getConfig()
            if mediaType != 'episode' and config.miniposters == True:
                process.addBanner(self, t, 'mini_4k', poster, size, mediaType, db)
            else:
                process.addBanner(self, t, 'banner_4k', poster, size, mediaType, db)
        else: logger.info(self.title+': does not need resolution banner')
        valid = process.finalCheck(self, poster, size)
        if valid == True:
            logger.debug('uploading poster')
            process.upload(self, poster)

    def checked(self, db):
        item = db.objects.filter(guid=self.guid).first()
        try: 
            checked = item.checked
        except AttributeError:
            checked = False
        return checked

    def updateChecked(self, db):
        item = db.objects.get(guid=self.guid)
        item.checked = True
        item.save()

    def human_readable_size(num, suffix="B"):
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    def dbUpdate(self, db, hdr, audio, mediaType):
        logger.debug('adding file to database')
        plex = item.getPlex()
        logger.debug(f"DBUpdate hdr:{hdr}, audio:{audio}")
        def connect_season_to_show(res, hdr, showGuid, seasonGuid, showTitle):
            from posters.models import show, season
            if type(hdr) == str:
                if hdr.lower() != 'none':
                    hdr = True
                else: hdr = False
            elif hdr == None:
                hdr = False
            try:
                s = show.objects.get(guid=showGuid)
                dbseason = season.objects.get(guid=seasonGuid)
                s.seasons.add(dbseason)
            except show.DoesNotExist:
                logger.warning(f"Show isn't in the database yet")
                show.objects.update_or_create(
                    guid=showGuid, 
                    defaults={'title':showTitle, 
                              'res':res, 
                              'hdr':hdr, 
                              'checked':False,
                              }
                    )
                s = show.objects.get(guid=showGuid)
                i = season.objects.get(guid=seasonGuid)
                s.seasons.add(i)
        def connect_episode_to_season(res, hdr):
            from posters.models import season
            try:
                s = season.objects.get(guid=self.parentGuid)
                i = db.objects.get(guid=self.guid)
                s.episodes.add(i)
            except season.DoesNotExist:
                logger.warning(f"Season isn't in the database yet")
                if type(hdr) == str:
                    if hdr.lower() != 'none':
                        hdr = True
                    else: hdr = False
                elif hdr == None:
                    hdr = False
                season.objects.update_or_create(
                    guid=self.parentGuid, 
                    defaults={'title':self.parentTitle, 
                              'res':res, 
                              'hdr':hdr, 
                              'checked':False,
                              }
                    )
                s = season.objects.get(guid=self.parentGuid)
                i = db.objects.get(guid=self.guid)
                s.episodes.add(i)
        try:
            url = "https://app.plex.tv/desktop#!/server/"+str(plex.machineIdentifier)+'/details?key=%2Flibrary%2Fmetadata%2F'+str(self.ratingKey)
        except: url = ''
        try:
            size = process.human_readable_size(self.media[0].parts[0].size)
            res = self.media[0].videoResolution
        except: 
            size = ''
            res = ''
        if mediaType == 'episode':
            i = db.objects.update_or_create(
                guid=self.guid, 
                defaults={
                'title':self.title, 
                'guid':self.guid, 
                'guids':self.guids, 
                'parentguid':self.parentGuid, 
                'grandparentguid':self.grandparentGuid, 
                'size':size, 
                'res':res, 
                'hdr':hdr, 
                'audio':audio, 
                'url':url, 
                'checked':False,
                'blurred':False
                })
            connect_episode_to_season(res, hdr)
            connect_season_to_show(res, hdr, self.grandparentGuid, self.parentGuid, self.grandparentTitle)
        elif mediaType =='film':
            defaults={'title':self.title, 
                  'guids':self.guids, 
                  'size':size,
                  'res':res, 
                  'hdr':hdr,
                  'audio': audio,
                  'url':url,
                  } 
            if audio == None and hdr == None:
                logger.debug('Not updating audio or hdr')
                defaults={'title':self.title, 
                          'guids':self.guids, 
                          'size':size,
                          'res':res, 
                          'url':url,
                          }
            if audio == None and hdr != None:
                logger.debug('Updating HDR but Not updating audio')
                defaults={'title':self.title, 
                          'guids':self.guids, 
                          'size':size,
                          'res':res, 
                          'hdr': hdr,
                          'url':url,
                          }  
            if hdr == None and audio != None:
                logger.debug('Updating audio but Not updating hdr')
                defaults={'title':self.title, 
                          'guids':self.guids, 
                          'size':size,
                          'res':res, 
                          'audio': audio,
                          'url':url,
                          }     
            db.objects.update_or_create(
                guid=self.guid, 
                defaults = defaults,
                )
        elif mediaType =='3d':
            db.objects.update_or_create(
                guid=self.guid, 
                defaults={'title':self.title, 
                          'guids':self.guids, 
                          'size':size,
                          'url':url, 
                          'checked':False,
                          }
                )            
        elif mediaType =='show' or mediaType == 'season':
            db.objects.update_or_create(
                guid=self.guid, 
                defaults={'title':self.title, 
                          'res':res, 
                          'hdr':hdr, 
                          'url':url,
                          'checked':False,
                          }
                )
            if mediaType == 'season':
                connect_season_to_show(res, hdr, self.parentGuid, self.guid, self.parentTitle)
                
    def finalCheck(self, poster, size):
        cropped = (1000,1500,2000,3000)
        new_poster = cv2.imread(poster, cv2.IMREAD_ANYCOLOR)
        new_poster = cv2.cvtColor(new_poster, cv2.COLOR_BGR2RGB)
        new_poster = Image.fromarray(new_poster)
        new_poster = new_poster.resize(size,Image.LANCZOS)
        new_poster = new_poster.crop(cropped)

        plex_poster = item.poster(self, '/tmp/check.png', size)
        plex_poster = cv2.imread(plex_poster, cv2.IMREAD_ANYCOLOR)
        plex_poster = cv2.cvtColor(plex_poster, cv2.COLOR_BGR2RGB)
        plex_poster = Image.fromarray(plex_poster)
        plex_poster = plex_poster.resize(size,Image.LANCZOS)
        plex_poster = plex_poster.crop(cropped)

        new_poster_hash = imagehash.average_hash(new_poster)
        plex_poster_hash = imagehash.average_hash(plex_poster)

        if new_poster_hash == plex_poster_hash:
            return True
        else:
            return False
        
    def upload(self, file):
        try:
            self.uploadPoster(filepath=file)
        except BadRequest as e:
            logger.error(self.title+': '+repr(e))
            
    def clear_old_posters():
        dirpath = '/tmp/'
        for files in os.listdir(dirpath):
            if files.endswith(".png"):
                os.remove(dirpath+files) 
        #dirpath = './app/static/img/tmp/'
        #for files in os.listdir(dirpath):
        #    if files.endswith(".png"):
        #        os.remove(dirpath+files) 

class file:
    def file_exists(file):
        try:
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, file)) == True:
                return True
            else: return False
        except: pass


    def isModified(self, db):
        filesize = self.media[0].parts[0].size
        result = db.objects.filter(guid=self.guid).first()
        if result != None:
            if str(result.size) == str(filesize):
                return False
            else: return True
        else: return True    

class tmdbPoster:
    def tmdbGuid(self):
        g = self[1:-1]
        g = re.sub(r'[*?:"<>| ]',"",g)
        g = re.sub("Guid","",g)
        g = g.split(",")
        f = filter(lambda a: "tmdb" in a, g)
        g = list(f)
        g = str(g[0])
        gv = [v for v in g if v.isnumeric()]
        g = "".join(gv)
        return g    

    def tmdbPosterPath(self, g, mediaType, episode, season):
        config, advancedConfig = item.getConfig()
        tmdb.api_key = config.tmdb_api
        if mediaType == 'film':
            tmdb_search = movie.details(movie_id=g)
            poster2_search = movie.images(movie_id=g)
            poster = tmdb_search.poster_path
            return poster
        elif mediaType == 'episode':
            if g == None:
                if self.grandparentTitle == '':
                    tmdb_search = tmdbtv.details(name=self.parentTitle, episode_num=episode, season_num=season)
                else:
                    tmdb_search = tmdbtv.details(name=self.grandparentTitle, episode_num=episode, season_num=season)
            else:
                tmdb_search = tmdbtv.details(tv_id=g, episode_num=episode, season_num=season)
            poster = tmdb_search.still_path 
            return poster
        elif mediaType == 'season':
            tmdb_search = tmdbSeason.details(tv_id=g,  season_num=season)
            poster = tmdb_search.poster_path
            return poster
        elif mediaType == 'show':
            tmdb_search = tmdbShow.details(tv_id=g)
            poster = tmdb_search.poster_path 
            return poster

    def getTmdbPoster(fname, poster):
        req = requests.get(poster_url_base+poster, stream=True)
        if req.status_code == 200:
            with open(fname, 'wb') as f:
                for chunk in req:
                    f.write(chunk)
            return fname
        else:
            logger.error("Can't get poster from TMDB")
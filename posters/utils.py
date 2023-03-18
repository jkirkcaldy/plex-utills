import cv2, imagehash
import requests
import re
from PIL import Image
from pathlib import PureWindowsPath, PurePosixPath
from pymediainfo import MediaInfo
import json
from plexapi.server import PlexServer
from .models import Plex
from django.conf import settings
import os
from django.core.files.storage import default_storage


class banners:
    def bannerTemplate(bannerType):
        if bannerType == 'banner_4k':
            Type = "static/banners/4K-Template.png"
        elif bannerType == 'mini_4k':
            Type = "static/banners/4K-mini-Template.png"
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
            Type = "static/banners/tv/4K.png"
        elif bannerType == 'hdr10':
            Type = "static/banners/tv/hdr10.png"
        elif bannerType == 'hdr':
            Type = "static/banners/tv/hdr.png"
        elif bannerType == 'dv':
            Type = "static/banners/tv/dolbyVision.png"
        elif bannerType == 'atmos':
            Type = "static/banners/tv/atmos.png"
        elif bannerType == 'dtsx':
            Type = "static/banners/tv/dtsx.png"
        banner_bg = Image.open("app/img/tv/Background.png")
        banner = Image.fromarray(cv2.imread(banner, Type, cv2.IMREAD_UNCHANGED))
        return banner_bg, banner
    
    def baseHash(bannerType):

        if bannerType == 'banner_4k':
            hash = "static/banners/chk-4k.png"
        elif bannerType == 'mini_4k':
            hash = "static/banners/chk-mini-4k2.png"
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
            dolbyVisionBanner = True
        else: dolbyVisionBanner = False
        if posterBannerHash[3] - banners.baseHash('hdr') <= 10:
            hdrBanner = True
        else: hdrBanner = False
        if posterBannerHash[3] - banners.baseHash('hdr10') <= 10:
            hdr10Banner = True 
        else: hdr10Banner = False    
        return dolbyVisionBanner, hdr10Banner, hdrBanner
    
    def audioBannerCheck(posterBannerHash):
        if posterBannerHash[2] - banners.baseHash('atmos') <= 10:
            atmosBanner = True
        else: atmosBanner = False
        if posterBannerHash[2] - banners.baseHash('dtsx') <= 10:
            dtsxBanner = True    
        else: dtsxBanner = False    
        return atmosBanner, dtsxBanner
    
    def resolutionBannerCheck(posterBannerHash):
        if posterBannerHash[0] - banners.baseHash('banner_4k') <= 10:
            wideBanner = True
        else: wideBanner = False
        if posterBannerHash[1] - banners.baseHash('mini_4k') <= 10:
            mini4kBanner = True 
        else: mini4kBanner = False
        return wideBanner, mini4kBanner       

class item:
    def getConfig():
        config = Plex.objects.filter(pk='1').first()
        return config
    
    def getPlex():
        p = Plex.objects.filter(pk='1').first()
        plex = PlexServer(p.plexurl, p.token)
        return plex
    
    def tmpPoster(self, mediaType):
        if mediaType == 'film':
            t = re.sub('plex://movie/', '', self.guid)
        elif mediaType == 'episode':
            t = re.sub('plex://episode/', '', self.guid)
        elif mediaType == 'season':
            t = re.sub('plex://season/', '', self.guid)
        tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')    
        return tmp_poster, t
    
    def libraries(mediaType):
        libraries = []
        config = item.getConfig()
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
        config = item.getConfig()
        p = PureWindowsPath(self.media[0].parts[0].file)
        p1 = re.findall('[A-Z]', p.parts[0])
        if p1 != []:
            file = PurePosixPath('/films', *p.parts[1:])
        if config.manualplexpath == 1:
            file = re.sub(config.manualplexpathfield, '/films', self.media[0].parts[0].file)
        else:
            file = re.sub(config.plexpath, '/films', self.media[0].parts[0].file)
        return file        
    
    def tmdb_guid(self):
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
    
    def getAudio(self, db):
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
        i = db.objects.filter(guid=self.guid).first()
        i.audio = str.lower(audio)
        i.save()
        return str.lower(audio)
    
    def getHdr(self, db):
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
        i = db.objects.filter(guid=self.guid).first()
        i.hdr = hdrVersion
        i.save()
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
        return fileName
    
    def scanFile(self, filePath, db):
        versions = ['dovi', 'hdr', 'hdr10', 'hdr10+']
        m = MediaInfo.parse(filePath, output='JSON')
        x = json.loads(m)
        hdr = item.getHdr(self, db)
        if 'HDR' in hdr:
            hdrVersion = x['media']['track'][1]['HDR_Format_Compatibility']
        elif any(h in hdr for h in versions):
            hdrVersion = hdr
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
            if 'TypeError' in e:
                pass
        i = db.objects.filter(guid=self.guid).first()
        i.hdr = str.lower(hdrVersion)
        i.audio = audio
        i.save()
        return str.lower(hdrVersion), str.lower(audio)
    
    def newPoster(self, poster, mediaType, t, db):

        dbPoster = db.objects.filter(guid=self.guid).first()
        try:
            bakPoster = imagehash.average_hash(Image.fromarray(cv2.imread(dbPoster.poster, cv2.IMREAD_UNCHANGED)))
            posterHash = banners.posterHash(poster)
            if posterHash - bakPoster > 7:
                newPoster = True
            else: newPoster = False
        except: newPoster = True
     
        if newPoster == True:
            name = mediaType+'/backup/'+t+'.png'
            if file.file_exists(name) == True:
                os.remove(settings.MEDIA_ROOT+'/'+name)
            with open(poster, 'rb') as f:
                f = default_storage.save(name, f)
            i = db.objects.filter(guid=self.guid).first()
            i.poster = name
            i.save()

        return newPoster

class process:
    def addBanner(self, t, bannerType, poster, size, mediaType, db):
        processedPoster = Image.open(poster) #Image.fromarray(cv2.imread(poster, cv2.COLOR_BGR2RGBA))
        processedPoster.resize(size,Image.LANCZOS)
        if mediaType != 'episode':
            banner = banners.bannerTemplate(bannerType)
        else:
            banner = banners.episodeBannerTemplate(bannerType)
        processedPoster.paste(banner, (0,0), banner)
        processedPoster.save(poster)
        name = mediaType+'/bannered/'+t+'_bannered.png'
        if file.file_exists(name) == True:
            os.remove(settings.MEDIA_ROOT+'/'+name)
        with open(poster, 'rb') as f:
            f = default_storage.save(name, f)
        dbPoster = db.objects.filter(guid=self.guid).first()
        dbPoster.bannered_poster = name
        dbPoster.checked = True
        dbPoster.save()

    def checked(self, db):
        film = db.objects.filter(guid=self.guid).first()
        return film.checked

    def dbUpdate(self, db):
        plex = item.getPlex()
        url = "https://app.plex.tv/desktop#!/server/"+str(plex.machineIdentifier)+'/details?key=%2Flibrary%2Fmetadata%2F'+str(self.ratingKey)
        size = self.media[0].parts[0].size
        res = self.media[0].videoResolution
        try:
            media = db.objects.filter(guid=self.guid).first()
            print(media.title+" exists")
        except Exception as e:
            print(repr(e))
            i = db(title=self.title, guid=self.guid, guids=self.guids, size=size, res=res, url=url)
            i.save()
 
    def finalCheck(self, poster, size):
        cropped = (1000,1500,2000,3000)
        new_poster = cv2.imread(poster, cv2.IMREAD_ANYCOLOR)
        new_poster = cv2.cvtColor(new_poster, cv2.COLOR_BGR2RGB)
        new_poster = Image.fromarray(new_poster)
        new_poster = new_poster.resize(size,Image.LANCZOS)
        new_poster = new_poster.crop(cropped)

        plex_poster = item.poster(self, 'tmp/check.png', size)
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
        self.uploadPoster(filepath=file)

        
class file:
    def file_exists(file):
        try:
            if os.path.exists(settings.MEDIA_ROOT+'/'+file) == True:
                return True
            else: return False
        except: pass
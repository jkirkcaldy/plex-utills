from posters.models import *

from posters.utils import banners, item, process, tmdbPoster, file
from django.conf import settings
from django.core.files.storage import default_storage
from celery_progress.backend import ProgressRecorder
from django.db.models import Q
import os
from PIL import Image
cutoff = 10
import logging
from celery import shared_task
from utils.models import Plex
from tautulli import RawAPI
from tmdbv3api import TMDb, Search, Movie, Discover, Season, Episode, TV
from plexapi.server import PlexServer
from PIL import ImageFilter
import shutil
tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
tmdb.api_key = '758d054ea2656332403b34471f1f2c5a'
search = Search()
movie = Movie()
discover = Discover()
logger = logging.getLogger(__name__)

@shared_task(bind=True, name='plex-utils.Posters4k')
def posters4k(self, webhooktitle, posterVar, mediaType):
    size=(2000,3000)
    errors = []
    plex = item.getPlex()
    libraries = item.libraries(mediaType)
    config, advancedConfig = item.getConfig()
    db = film
    for library in libraries:
        key = [media.key for media in library.search(title=webhooktitle)]
        n = len(key)
        for x in range(n):
            for f in plex.fetchItems(key[x]):
                    logger.info(f.title)
                    process.dbUpdate(f, db, None, None, mediaType)
                    checked = process.checked(f, db)
                    tmpPoster, t = item.tmpPoster(f, mediaType)
                    filepath = item.sanitiseFilepath(f)
                    if checked == True:
                        poster = item.poster(f, tmpPoster, size)
                        newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)
                    else: newPoster = 'unknown'
                    if checked == False or newPoster == True or posterVar != None:
                        logger.info('PROCESSING')
                        filepath = item.sanitiseFilepath(f)

                        res = f.media[0].videoResolution
                        if config.skip_media_info == False:
                            hdr = item.getHdr(f, db)
                            audio = item.getAudio(f, db)
                            hdr, audio = item.scanFile(f, filepath, db, hdr, audio)
                        else:
                            hdr = item.getHdr(f, db)
                            audio = item.getAudio(f, db)
                        if res == '4k' or hdr != 'none' or 'atmos' in audio or 'dtsx' in audio:
                            process.dbUpdate(f, db, hdr, audio, mediaType)
                            #logger.debug(hdr+' - '+audio)
                            
                            if posterVar != '':
                                tmdbGuid = tmdbPoster.tmdbGuid(f.guids)
                                tmdbPosterPath = tmdbPosterPath(f, tmdbGuid, mediaType, None, None)
                                poster = tmdbPoster.getTmdbPoster(tmpPoster, posterVar)
                                newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)
                            else:
                                poster = item.poster(f, tmpPoster, size)
                                newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)
                            
                            if newPoster == True:
                                print(hdr)
                                if 'dovi' in hdr or 'hdr' in hdr:
                                    dolbyVisionBanner = hdrBanners[0]
                                    hdr10Banner = hdrBanners[1]
                                    hdrBanner = hdrBanners[2]
                                    process.dbUpdate(f, db, hdr, None, mediaType)
                                    print(hdr)
                                    if hdr == 'dovi' and dolbyVisionBanner == 'False':
                                        #logger.debug('adding DoVi banner')
                                        process.addBanner(f, t, 'dv', poster, size, mediaType, db) 
                                    elif 'hdr10+' in hdr and hdr10Banner == 'False':
                                        #logger.debug('adding hdr10+ banner')
                                        process.addBanner(f, t, 'hdr10', poster, size, mediaType, db)
                                    elif 'hdr' in hdr and '+' not in hdr and hdrBanner == 'False':
                                        #logger.debug('adding hdr banner')
                                        process.addBanner(f, t, 'hdr', poster, size, mediaType, db) 
                                else: logger.info(f.title+': does not need hdr banner')
                                if ('atmos' in audio or 'dts:x' in audio):
                                    atmosBanner = audioBanners[0]
                                    dtsxBanner = audioBanners[1]
                                    process.dbUpdate(f, db, None, audio, mediaType)
                                    if audio == 'atmos' and atmosBanner == 'False':
                                        process.addBanner(f, t, 'atmos', poster, size, mediaType, db)
                                    if audio == 'dts:x' and dtsxBanner == 'False':
                                        process.addBanner(f, t, 'dtsx', poster, size, mediaType, db)
                                else: logger.info(f.title+': does not need audio banner')
                                if res == '4k':
                                    wideBanner = [0]
                                    mini4kBanner = resBanners[1]
                                    process.dbUpdate(f, db, None, None, mediaType)
                                    if config.miniposters == True and mini4kBanner == 'False':
                                        process.addBanner(f, t, 'mini_4k', poster, size, mediaType, db)
                                    elif config.miniposters == False and wideBanner == 'False':
                                        process.addBanner(f, t, 'banner_4k', poster, size, mediaType, db)
                                else: logger.info(f.title+': does not need resolution banner')
                                valid = process.finalCheck(f, poster, size)
                                if valid == True:
                                    process.upload(f, poster) 

                            else:
                                logger.info('Looks like '+f.title+' has already been processed')
    process.clear_old_posters()
    logger.info('4k Poster script has finished for Films')
    if errors:
        logger.error('The following errors occurred:')
        for e in errors:
            logger.error(e)

@shared_task(bind=True, name='plex-utils.Posters4kTV')
def posters4kTV(self, webhookGuid, posterVar, mediaType):
    size=(1280,720)
    logger.info('Starting TV Posters')
    errors = []
    plex = item.getPlex()
    libraries = item.libraries(mediaType)
    config, advancedConfig = item.getConfig()
    db = episode
    for library in libraries:
        if config.tvPosterQuickScan == True:
            advancedFilters = {
                'or': [
                    {'resolution': '4k'},
                    {'hdr': True}
                ],
            }
            if webhookGuid != None:
                key = [media.key for media in library.search(libtype=mediaType, guid=webhookGuid, filters=advancedFilters)]
            else:
                key = [media.key for media in library.search(libtype=mediaType, filters=advancedFilters)]
        else:
            if webhookGuid != None:
                key = [media.key for media in library.search(libtype=mediaType, guid=webhookGuid)]
            else:
                key = [media.key for media in library.search(libtype=mediaType)]
        n = len(key)
        for x in range(n):
            for f in plex.fetchItems(key[x]):
                logger.info(f.title)
                process.dbUpdate(f, db, 'None', 'None', mediaType)
                checked = process.checked(f, db)
                tmpPoster, t = item.tmpPoster(f, mediaType)
                filepath = item.sanitiseFilepath(f)
                modified = file.isModified(f, db)
                if checked == True:
                    poster = item.poster(f, tmpPoster, size)
                    #logger.debug('got poster')
                    newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)
                    #logger.debug(newPoster)
                else: newPoster = 'unknown'
                if checked == False or newPoster == True or modified == True or posterVar != None:
                    logger.info('PROCESSING')
                    filepath = item.sanitiseFilepath(f)
                    res = f.media[0].videoResolution
                    if config.skip_media_info == False:
                        hdr = item.getHdr(f, db)
                        audio = item.getAudio(f, db)
                        hdr, audio = item.scanFile(f, filepath, db, hdr, audio)
                    else:
                        hdr = item.getHdr(f, db)
                        audio = item.getAudio(f, db)
                    if res == '4k' or hdr != 'none' or 'atmos' in audio or 'dtsx' in audio:
                        #logger.debug(hdr+' - '+audio)
                        if posterVar != None:
                            tmdbGuid = tmdbPoster.tmdbGuid(f.guids)
                            tmdbPosterPath = tmdbPosterPath(f, tmdbGuid, mediaType, None, None)
                            poster = tmdbPoster.getTmdbPoster(tmpPoster, posterVar)
                            newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)
                        else:
                            poster = item.poster(f, tmpPoster, size)
                            newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, poster, mediaType, t, db, size)

                        if newPoster == True:
                            banners.episodeBannerBackground(poster, size)
                            process.bannerDecisions(f, res, resBanners ,hdr, hdrBanners, audio, audioBanners, t, poster, size, mediaType, db)
                        else:
                            logger.info('Looks like '+f.title+' has already been processed')                                 
                process.updateChecked(f, db)
    process.clear_old_posters()
    logger.info('4k Poster script has finished for Episodes')
    if errors:
        logger.error('The following errors occurred:')
        for e in errors:
            logger.error(e)

@shared_task(bind=True, name='plex-utils.SeasonShowPosters')
def season_show_posters(self):
    logger.info('Starting Season and Show Posters')
    portraitSize = (2000,3000)
    plex = item.getPlex()
    libraries = item.libraries('episode')
    config, advancedConfig = item.getConfig()
    for library in libraries:

        episodes = episode.objects.filter(
            Q(res='4k') | ~Q(hdr='none') | ~Q(hdr='unknown')
            )
        for episodeDbItem in episodes:
            seasonGuid = episodeDbItem.parentguid
            res = episodeDbItem.res
            if episodeDbItem.hdr.lower() != 'none':
                hdr = True
            else:
                hdr = False
            logger.debug(res)
            logger.debug(hdr)
            newSeasonPoster = False
            seasonItem = item.getParent(library, seasonGuid, 'season')
            tmpPoster, seasonT = item.tmpPoster(seasonItem, 'season')
            seasonPoster = item.poster(seasonItem, tmpPoster, portraitSize)
            try:
                seasonDbItem = season.objects.get(guid=seasonGuid)
                if res == '4k':
                    seasonDbItem.res = '4k'
                if hdr != False:
                    seasonDbItem.hdr = True
                seasonDbItem.save()                            
                seasonDbItem.episodes.add(episodeDbItem)
            except Exception as e:
                name = 'season/backup/'+seasonT+'.png'
                if file.file_exists(name) == True:
                    os.remove(settings.MEDIA_ROOT+'/'+name)
                with open(seasonPoster, 'rb') as fItem:
                    fItem = default_storage.save(name, fItem)
                seasonDbItem = season(title=seasonItem.title, guid=seasonItem.guid, poster=fItem, checked=False)
                seasonDbItem = season(title=seasonItem.title, guid=seasonItem.guid, res=res, hdr=hdr, poster=fItem, checked=False)
                seasonDbItem.save()               
                seasonDbItem.episodes.add(episodeDbItem)
            newSeasonPoster, seasonhdrBanners, seasonaudioBanners, seasonresBanners = item.newPoster(seasonItem, seasonPoster, 'season', seasonT, season, portraitSize)
            if newSeasonPoster == True or seasonDbItem.checked == False:
                process.bannerDecisions(seasonItem, res, seasonresBanners ,hdr, seasonhdrBanners, 'None', seasonaudioBanners, seasonT, seasonPoster, portraitSize, 'season', season)  
            ##get Show and add it to the database if it doesn't exist already
            showGuid = episodeDbItem.grandparentguid
            newShowPoster = False
            showItem = item.getParent(library, showGuid, 'show')
            tmpPoster, showT = item.tmpPoster(showItem, 'show')
            showPoster = item.poster(showItem, tmpPoster, portraitSize)
            try:
                showDbItem = show.objects.get(guid=showGuid)
                if res == '4k':
                    showDbItem.res = '4k'
                if hdr != False:
                    showDbItem.hdr = True
                showDbItem.save()
                showDbItem.seasons.add(seasonDbItem)
            except:
                name = 'show/backup/'+showT+'.png'
                if file.file_exists(name) == True:
                    os.remove(settings.MEDIA_ROOT+'/'+name)
                with open(showPoster, 'rb') as fItem:
                    fItem = default_storage.save(name, fItem)
                showDbItem = show(title=showItem.title, guid=showItem.guid, res=res, hdr=hdr, poster=fItem, checked=False)
                showDbItem.save()                            
                showDbItem.seasons.add(seasonDbItem)
            newShowPoster, showhdrBanners, showaudioBanners, showresBanners = item.newPoster(showItem, showPoster, 'show', showT, show, portraitSize)
            if newShowPoster == True or showDbItem.checked == False:
                process.bannerDecisions(showItem, res, showresBanners ,hdr, showhdrBanners, 'None', showaudioBanners, showT, showPoster, portraitSize, 'show', show)  
            #process.updateChecked(showItem, show)

@shared_task(bind=True, name='plex-utils.RestoreFilmPosters')
def restoreFilms(self):
    films = film.objects.all()
    
    for f in films:
        logger.info(f.title)
        libraries = item.libraries('film')
        for library in libraries:
            for i in library.search(guid=f.guid):
                logger.info(i.title)
                tmpPoster, t = item.tmpPoster(i, 'film')
                path = os.path.join(settings.MEDIA_ROOT, str(f.poster))

                img = Image.open(path)
                img.save(tmpPoster)
                process.upload(i, tmpPoster)
    process.clear_old_posters()

@shared_task(bind=True, name='plex-utils.RestorePostersfromTMDB')
def tmdbRestore(self, mediaType, size):
    errors = []
    plex = item.getPlex()
    libraries = item.libraries(mediaType)
    config, advancedConfig = item.getConfig()
    db = film

    for library in libraries:
        key = [film.key for film in library.search()]
        n = len(key)
        for x in range(n):
            for f in plex.fetchItems(key[x]):
                try:
                    #logger.debug(f.title)
                    tmpPoster, t = item.tmpPoster(f, mediaType)
                    #logger.debug(tmpPoster)
                    g = tmdbPoster.tmdbGuid(str(f.guids))
                    #logger.debug(g)
                    tmdbPosterPath = tmdbPoster.tmdbPosterPath(f, g, 'film', None, None)
                    #logger.debug(tmdbPosterPath)
                    poster = tmdbPoster.getTmdbPoster(tmpPoster, tmdbPosterPath)
                    #logger.debug(poster)
                    process.upload(f, poster)
                    logger.info('Uploaded poster')
                except Exception as e:
                    logger.error(repr(e))

@shared_task(bind=True, name='plex-utils.RestoreTVPostersfromTMDB')
def tmdbTvRestore(self, mediaType, size):
    errors = []
    plex = item.getPlex()
    libraries = item.libraries(mediaType)
    config, advancedConfig = item.getConfig()
    for library in libraries:
        for s in  library.search(libtype='season'):
            try:
                g = tmdbPoster.tmdbGuid(item.getShowGuid(s, library, s.parentGuid))
                # season
                tmpPoster, t = item.tmpPoster(s, 'season')
                tmdbPosterPath = tmdbPoster.tmdbPosterPath(s, g, 'season', None, s.index)
                #logger.debug(tmdbPosterPath)
                poster = tmdbPoster.getTmdbPoster(tmpPoster, tmdbPosterPath)
                #logger.debug(poster)
                process.upload(s, poster)
                logger.info('Uploaded poster')
            except Exception as e:
                errors.append(s.title+': '+repr(e))
                logger.error(s.title)
                pass
        for sh in library.search(libtype='show'):
            try:
                tmpPoster, t = item.tmpPoster(sh, 'show')
                # show
                g = tmdbPoster.tmdbGuid(str(sh.guids))
                tmdbPosterPath = tmdbPoster.tmdbPosterPath(sh, g, 'show', None, None)
                #logger.debug(tmdbPosterPath)
                poster = tmdbPoster.getTmdbPoster(tmpPoster, tmdbPosterPath)
                #logger.debug(poster)
                process.upload(sh, poster)
                logger.info('Uploaded poster')
                #logger.debug(tmpPoster)   
            except Exception as e:
                errors.append(sh.title+': '+repr(e))
                logger.error(sh.title)    
                pass        
        for f in library.search(libtype='episode'):
                try:
                    #logger.debug(f.title)
                    tmpPoster, t = item.tmpPoster(f, mediaType)
                    g = tmdbPoster.tmdbGuid(item.getShowGuid(f, library, f.grandparentGuid))
                    #logger.debug(g)
                    # episode
                    tmdbPosterPath = tmdbPoster.tmdbPosterPath(f, g, 'episode', f.index, f.parentIndex)
                    #logger.debug(tmdbPosterPath)
                    poster = tmdbPoster.getTmdbPoster(tmpPoster, tmdbPosterPath)
                    #logger.debug(poster)
                    process.upload(f, poster)
                    logger.info('Uploaded poster')
                except Exception as e:
                    errors.append(f.title+': '+repr(e))
                    logger.error(repr(e)) 
                    pass
    for error in errors:
        logger.error(error)               

def getmtime():
    f = film.objects.all()
    errors = []
    plex = item.getPlex()
    libraries = item.libraries('film')
    config, advancedConfig = item.getConfig()
    for i in f:
        print(i.guid)
        for library in libraries:
            for plexFilm in library.search(guid=i.guid):
                path = item.sanitiseFilepath(plexFilm)
                print(path)
                mtime = file.getMtime(path)
                i.mtime = mtime
                i.save()

@shared_task(bind=True, name='plex-utils.autocollections')
def autocollections(self):
    logger.info('Autocollections has started')
    config = Plex.query.filter(pk=1)
    plex = item.getPlex()
    tmdb.api_key = config.tmdb_api
    lib = config.filmslibrary.split(',')
    films = plex.library.section()
    for l in lib:
        for f in films(l.lstrip()).search():
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
                if config.tautulli_api != None:
                    try:
                        tautulli_api = RawAPI(base_url=config.tautulli_server, api_key=config.tautulli_api)
                        i=tautulli_api.get_home_stats(stats_type='plays', stat_id='top_movies')
                        x = json.dumps(tautulli_api.get_home_stats(stats_type='plays', stat_id='top_movies'))
                        i=json.loads(x)
                        top_watched=i["rows"][0]["title"]
                        tw_year=i["rows"][0]["year"]
                        logger.debug('Top watched film is: '+top_watched)
                        a = search.movies({ "query": top_watched, "year": tw_year })
                        def get_id():
                            for b in a:
                                i = b.id
                                return i
                        i = get_id()
                        rec = movie.recommendations(movie_id=i)
                        for r in rec:
                            title = r.title
                            logger.debug(title)
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
                                for chunk in img:
                                    f.write(chunk)                            
                                #shutil.copyfileobj(img.raw, f)
                        c.delete()
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': 'Marvel Studios'})
                        d = films.collection(collection)
                        d.uploadPoster(filepath='/tmp/poster.png')
                    if config.default_poster == True:
                        c.uploadPoster(filepath='app/img/collections/mcu_poster.png')
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': 'Marvel Studios'})
                    d = films.collection(collection)
                    if config.default_poster == True:
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
                                for chunk in img:
                                    f.write(chunk)                            
                                #shutil.copyfileobj(img.raw, f)
                        c.delete()
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': collection})
                        d = films.collection(collection)
                        d.uploadPoster(filepath='/tmp/poster.png')
                    if config.default_poster == True:
                        c.uploadPoster(filepath='app/img/collections/pixar_poster.jpeg')                    
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': collection})
                    d = films.collection(collection)
                    if config.default_poster == True:
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
                                for chunk in img:
                                    f.write(chunk)                             
                                #shutil.copyfileobj(img.raw, f)
                        c.delete()
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': collection})
                        d = films.collection(collection)
                        d.uploadPoster(filepath='/tmp/poster.png')
                    if config.default_poster == True:
                        c.uploadPoster(filepath='app/img/collections/disney_poster.jpeg') 
                except plexapi.exceptions.NotFound:
                    plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'studio': collection})
                    d = films.collection(collection)
                    if config.default_poster == True:
                        d.uploadPoster(filepath='app/img/collections/disney_poster.jpeg')
                logger.info("Disney Collection has finished")
            def audio_collections():
                def atmos():
                    collection = 'Dolby Atmos'
                    try:
                        c = films.collection(title=collection)
                    except plexapi.exceptions.NotFound:
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'label': collection})
                        d = films.collection(collection)
                        if config.default_poster == True:
                            d.uploadPoster(filepath='app/img/collections/Atmos_Poster.png') 
                    logger.info("Dolby Atmos Collection has finished") 
                def dtsx():
                    collection = 'DTS:X'
                    try:
                        c = films.collection(title=collection)
                    except plexapi.exceptions.NotFound:
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'label': collection})
                        d = films.collection(collection)
                        if config.default_poster == True:
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
                        plex.createCollection(section=config.filmslibrary, title=collection, smart=True, filters={'label': collection})
                        d = films.collection(collection)
                        if config.default_poster == True:
                            d.uploadPoster(filepath='app/img/collections/dolby_vision_Poster.png') 
                    logger.info("Dolby Vision Collection has finished")
                dolby_vision() 
            if config.autocollections == True:
                audio_collections()
                HDR_collections()
            if config.disney == True:
                disney()
            if config.pixar == True:
                pixar()
            if config.mcu_collection == True:
                MCU()                
            if config.tr_r_p_collection == True:
                popular()
                top_rated()
                recommended() 
            logger.info("Auto Collections has finished")

@shared_task(bind=True, name='plex-utils.Hide4K')
def hide4k(self):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdb.api_key = config.tmdb_api
    lib = config.filmslibrary.split(',')
    for l in lib:
        films = plex.library.section(l.lstrip())
        for f in films.search():
            if config[0].hide4k == 1:
                logger.info("Hide-4K: Hide 4k films script starting now")
                added = films.search(resolution='4k', sort='addedAt')
                optimized = [o.title for o in plex.optimizedItems()]
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
                                if movie.title not in optimized:
                                    movie.optimize(target='Custom', deviceProfile="Universal Mobile", videoQuality=10)
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
            
@shared_task(bind=True, name='plex-utils.spoilers')
def blurSpoilers(self, guid):
    mediaType = 'episode'
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdb.api_key = config.tmdb_api
    lib = config.tvlibrary.split(',')
    logger.info('Starting spoiler script')
    progress_recorder = ProgressRecorder(self)
    progress = 0
    if config.spoilers == True:
        for l in lib:
            if guid != None:
                episodes = plex.library.section(l.lstrip()).search(guid=guid, libtype='episode')
                total = len(episodes)
                for ep in episodes:
                    logger.debug(f'{ep.title}: spoiler removing blur')
                    dbep = episode.objects.filter(guid=ep.guid).first()
                    if dbep:
                        try:
                            process.upload(ep, os.path.join('/config', dbep.bannered_poster))
                            episode.objects.filter(guid=ep.guid).update(blurred=False)
                        except: 
                            try:
                                process.upload(ep, os.path.join('/config', dbep.poster))
                                episode.objects.filter(guid=ep.guid).update(blurred=False)
                                posters4kTV.delay(guid, None, mediaType, (1280,720))
                            except Exception as e:
                                logger.error(f'Spoiler restore: {repr(e)}')
                    progress += 1
                    progress_recorder.set_progress(progress, total, description='Spoilers Progress')
            else:
                episodes = plex.library.section(l.lstrip()).search(unwatched=True, libtype='episode')
                total = len(episodes)
                for ep in episodes:
                    logger.debug(f'{ep.title}: spoiler')
                    tmpPoster, t = item.tmpPoster(ep, mediaType)
                    name = f'backup/{mediaType}/backup/{t}.png'
                    dbep = episode.objects.filter(guid=ep.guid).first()
                    if dbep:
                        logger.debug('item is in database')
                        if dbep.poster:
                            posterExists = os.path.exists(os.path.join('/config', dbep.poster))
                        else:
                            posterExists = False
                        if dbep.blurred == False and dbep.bannered_poster == None and posterExists == True:
                            blurPoster = item.blurposter(ep, tmpPoster, (1280,720))
                            episode.objects.filter(guid=ep.guid).update(blurred=True)
                            process.upload(ep, tmpPoster)
                        elif dbep.blurred == False and dbep.bannered_poster != None and posterExists == True:
                            original = Image.open(os.path.join('/config', dbep.poster))
                            blurred_image = original.filter(ImageFilter.GaussianBlur(30))
                            blurred_image.save(tmpPoster)
                            episode.objects.filter(guid=ep.guid).update(blurred=True)
                            process.upload(ep, tmpPoster)
                        elif dbep.blurred == True: 
                            logger.debug(f'{ep.title} is blurred')
                            if ep.viewCount >= 1:
                                try:
                                    process.upload(ep, os.path.join('/config', dbep.bannered_poster))
                                except: 
                                    try:
                                        process.upload(ep, os.path.join('/config', dbep.poster))
                                        episode.objects.filter(guid=ep.guid).update(blurred=False)
                                        posters4kTV.delay(guid, None, mediaType, (1280,720))
                                    except Exception as e:
                                        logger.error(f'Spoiler restore: {repr(e)}')
                        elif posterExists == False:
                            logger.debug("Poster does not exist")
                            poster = item.poster(ep, tmpPoster, (1280, 720))
                            path = os.path.join('/config', name)
                            shutil.copy(poster, path)
                            original = Image.open(tmpPoster)
                            blurred_image = original.filter(ImageFilter.GaussianBlur(30))
                            blurred_image.save(tmpPoster)
                            episode.objects.update_or_create(
                                guid=ep.guid, 
                                defaults={
                                    'poster':name,
                                    'blurred':True
                                })
                            process.upload(ep, tmpPoster)
                        else:
                            logger.debug("Something is wrong and I can't process this episode.")
                    else:
                        logger.debug('item is not in database')
                        poster = item.poster(ep, tmpPoster, (1280, 720))
                        shutil.copy(poster, os.path.join('/config', name))
                        episode.objects.update_or_create(
                            guid=ep.guid, 
                            defaults={
                            'title':ep.title, 
                            'guid':ep.guid, 
                            'guids':ep.guids, 
                            'parentguid':ep.parentGuid, 
                            'grandparentguid':ep.grandparentGuid, 
                            'blurred':True
                            })
                        item.savePoster(ep, mediaType, t, tmpPoster, episode)
                        blurPoster = item.blurposter(ep, tmpPoster, (1280,720))
                        process.upload(ep, blurPoster)
                    process.clear_old_posters()
                    progress += 1
                    progress_recorder.set_progress(progress, total, description='Spoilers Progress')
        logger.info("Spoilers task finished")
                    
    else: 
        logger.info('Spoiler Script disabled.')           
                
@shared_task(bind=True, name='plex-utils.posters3d')
def posters3d(self):
    errors = []
    plex = item.getPlex()
    mediaType = '3d'
    libraries = item.libraries(mediaType)
    config, advancedConfig = item.getConfig()
    size = (2000,3000)
    db = film3d
    for library in libraries:
        for f in library.search():
            logger.info(f.title)
            process.dbUpdate(f, db, None, None, mediaType)
            checked = process.checked(f, db)
            tmpPoster, t = item.tmpPoster(f, mediaType)
            filepath = item.sanitiseFilepath(f)
            if checked == True:
                poster = item.poster(f, tmpPoster, size)
                newPoster, banner3d = item.new3dPoster(f, poster, mediaType, t, db, size)
                if newPoster == True and config.miniposters == True:
                    process.addBanner(f, t, 'mini_3d', poster, size, mediaType, db) 
                elif newPoster == True and config.miniposters == False:
                    process.addBanner(f, t, 'banner_3d', poster, size, mediaType, db)
            else:
                if config.miniposters == True:
                    process.addBanner(f, t, 'mini_3d', poster, size, mediaType, db) 
                elif config.miniposters == False:
                    process.addBanner(f, t, 'banner_3d', poster, size, mediaType, db)
            valid = process.finalCheck(f, poster, size)
            if valid == True:
                process.upload(f, poster)
                    

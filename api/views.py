from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse, StreamingHttpResponse
from django.conf import settings
from plexapi.server import PlexServer
import plexapi
import shutil
from django.core import serializers
from posters.models import film, episode, season, show
from posters import classes
from tautulli import RawAPI
from tmdbv3api import TMDb, Search, Movie, Discover, Season, Episode, TV
from utils.models import Plex
from posters.tasks import *
import json
import logging
from api import api as API
from posters.utils import *

from django.views.decorators.csrf import csrf_exempt

version = '23.10'
logger = logging.getLogger(__name__)

tmdb = TMDb()
poster_url_base = 'https://www.themoviedb.org/t/p/original'
tmdb.api_key = '758d054ea2656332403b34471f1f2c5a'
search = Search()
movie = Movie()
discover = Discover()
b_dir = '/config/backup/' 



size = (2000,3000)
bannerbox= (0,0,2000,246)
mini_box = (0,0,350,275)
hdr_box = (0,1342,493,1608)
a_box = (0,1608,493,1766)
cutoff = 10
from django_celery_beat.models import PeriodicTask
from plex_utils.celery import app as celery_app

def delete_database(request, var):
    if var == 'films':
        film.objects.all().delete()
        logger.debug('films')
    elif var == 'episodes':
        episode.objects.all().delete()
        logger.debug('episodes')
    elif var == 'seasons':
        season.objects.all().delete()
        logger.debug('seasons')
    elif var == 'shows':
        show.objects.all().delete()
        logger.debug('shows')
    
    response = HttpResponse(json.dumps({'message': 'Database deleted!'}))
    response.status_code = 200
    return response

def get_db_films(request):
    films = film.objects.all()
    json = serializers.serialize('json', films)
   
    return HttpResponse(json, content_type='application/json')

def get_db_episodes(request):
    episodes = episode.objects.all().exclude(bannered_poster__exact='')
    json = serializers.serialize('json', episodes)
    return HttpResponse(json, content_type='application/json')

def get_db_seasons(request):
    seasons = season.objects.all().exclude(poster__exact='')
    json = serializers.serialize('json', seasons)
    return HttpResponse(json, content_type='application/json')

def get_db_shows(request):
    shows = show.objects.all().exclude(poster__exact='')
    json = serializers.serialize('json', shows)
    return HttpResponse(json, content_type='application/json')

# scripts

def runTask(request, taskID):
    task = PeriodicTask.objects.get(id=taskID)  
    celery_app.send_task(task.task, kwargs=json.loads(task.kwargs), queue='plex-utils')

    return redirect('/api/logs')

def Posters4k(request):
    size = (2000,3000)
    task = posters4k.delay(None, None, 'film', size)
    return redirect('/api/logs')

def tvposters4k(request):
    size = (1280,720)
    task = posters4kTV.delay(None, 'episode', size)
    return redirect('/api/logs')

def tvseason_showposters(request):
    task = season_show_posters.delay(None, 'episode', size)
    return redirect('/api/logs')

def posters3d(request):
    task = posters3d.delay()
    return redirect('/api/logs')

def runRestore(request):
    task = runRestore.delay()
    return redirect('/api/logs')

def restore_from_database(request):
    task = restoreFilms.delay()
    return redirect('/api/logs')

def runTmdbRestore(request):
    size = (2000,3000)
    task = tmdbRestore.delay('film', size)
    return redirect('/api/logs')

def runTmdbTvRestore(request):
    size = (2000,3000)
    task = tmdbTvRestore.delay('episode', size)
    return redirect('/api/logs')

def spoilerscript(request):
    task = blurSpoilers.delay(None)
    context = {
        'version': version,
        'task_id':task.task_id
    }
    return render(request, 'app/script_log_viewer.html', context)
    #return redirect('/api/logs', {'task_id':task.task_id})

# logs
def Logs(request):
    context = {
        'version': version
    }
    return render(request, 'app/logs.html', context)

def getTaskLogs(request):
    def script_generate():
        with open('/logs/script.log', "rb") as f:
            #for line in reversed(list(f)):
            for line in (f.readlines() [-30:]):
                yield line
    return StreamingHttpResponse(script_generate())

def getSystemLogs(request):
    def script_generate():
        with open('/logs/django.log', "rb") as f:
            for line in (f.readlines() [-30:]):
                yield line
    return StreamingHttpResponse(script_generate())



def getNginxErrorLogs(request):
    def streamTaskLogs():
         with open('/logs/nginx/plex-utills.error.log', "r") as f:
            for line in (f.readlines() [-30:]):
                    yield line
    return StreamingHttpResponse(streamTaskLogs())

def getNginxAccessLogs(request):
    def streamTaskLogs():
         with open('/logs/nginx/plex-utills.access.log', "r") as f:
            for line in (f.readlines() [-30:]):
                    yield line
    return StreamingHttpResponse(streamTaskLogs())

def get_film_posters():
    config = Plex.objects.get(pk='1')
    plex = PlexServer(config.plexurl, config.token)
    films = json.dumps({'films': []})
    jsonfilm = json.loads(films)
    lib = config.filmslibrary.split(',')
    for l in lib:
        for f in plex.library.section(l.lstrip()).search():
            film = {}
            film['title'] = f.title
            film['guid'] = f.guid
            film['poster'] = f.thumbUrl
            jsonfilm['films'].append(film)
        return json.dumps(jsonfilm, indent=4)

def get_show_posters():
    config = Plex.objects.get(pk='1')
    plex = PlexServer(config.plexurl, config.token)
    shows = json.dumps({'shows': []})
    jsonshow = json.loads(shows)
    lib = config.tvlibrary.split(',')
    for l in lib:
        for s in plex.library.section(l.lstrip()).search():
            show = {}
            show['title'] = s.title
            show['guid'] = s.guid
            show['poster'] = s.thumbUrl
            jsonshow['shows'].append(show)
        return json.dumps(jsonshow, indent=4) 

def get_season_posters(guid):
    config = Plex.objects.get(pk='1')
    plex = PlexServer(config.plexurl, config.token)
    seasons = json.dumps({'seasons': []})
    jsonseason = json.loads(seasons)
    lib = config.tvlibrary.split(',')
    for l in lib:
        for s in plex.library.section(l.lstrip()).search(libtype='season', filters={"show.guid":guid}):
            season = {}
            season['title'] = s.title
            season['guid'] = s.guid
            season['poster'] = s.thumbUrl
            jsonseason['seasons'].append(season)
        return json.dumps(jsonseason, indent=4) 
  
def get_episode_posters(guid):
    config = Plex.objects.get(pk='1')
    plex = PlexServer(config.plexurl, config.token)
    episodes = json.dumps({'episodes': []})
    jsonep = json.loads(episodes)
    lib = config.tvlibrary.split(',')
    for l in lib:
        for s in plex.library.section(l.lstrip()).search(libtype='episode', filters={"season.guid":guid}):
            episode = {}
            episode['title'] = s.title
            episode['guid'] = s.guid
            episode['poster'] = s.thumbUrl
            jsonep['episodes'].append(episode)
        return json.dumps(jsonep, indent=4)  


def get_tmdb_show_posters(var):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdbtvs = TV()
    posters = []
    lib = config.tvlibrary.split(',')
    for l in lib:
        for show in plex.library.section(l).search(libtype='show', guid=var):
            g = str(show.guids)
            g = g[1:-1]
            g = re.sub(r'[*?:"<>| ]',"",g)
            g = re.sub("Guid","",g)
            g = g.split(",")
            f = filter(lambda a: "tmdb" in a, g)
            g = list(f)
            g = str(g[0])
            gv = [v for v in g if v.isnumeric()]
            g = "".join(gv)
            tmdb_search = tmdbtvs.images(tv_id=g, include_image_language='en')
            for poster in tmdb_search.posters:
                posters.append(poster.file_path)
    return posters

def get_tmdb_season_posters(var):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdbtvs = Season()
    posters = []
    lib = config.tvlibrary.split(',')
    for l in lib:
        for season in plex.library.section(l).search(libtype='season', guid=var):
            g = str([s.guids for s in plex.library.section(l).search(libtype='show', guid=season.parentGuid)])
            g = g[1:-1]
            g = re.sub(r'[*?:"<>| ]',"",g)
            g = re.sub("Guid","",g)
            g = g.split(",")
            f = filter(lambda a: "tmdb" in a, g)
            g = list(f)
            g = str(g[0])
            gv = [v for v in g if v.isnumeric()]
            g = "".join(gv)
            tmdb_search = tmdbtvs.images(tv_id=g, season_num=season.index, include_image_language='en')
            for poster in tmdb_search:
                posters.append(poster.file_path)
    return posters

def get_tmdb_episode_posters(var):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdbtv = Episode()
    posters = []
    lib = config.tvlibrary.split(',')
    for l in lib:
        for episode in plex.library.section(l).search(libtype='episode', guid=var):
            g = str([s.guids for s in plex.library.section(l).search(libtype='show', guid=episode.grandparentGuid)])
            g = g[1:-1]
            g = re.sub(r'[*?:"<>| ]',"",g)
            g = re.sub("Guid","",g)
            g = g.split(",")
            f = filter(lambda a: "tmdb" in a, g)
            g = list(f)
            g = str(g[0])
            gv = [v for v in g if v.isnumeric()]
            g = "".join(gv)
            tmdb_search = tmdbtv.images(tv_id=g, season_num=episode.parentIndex, episode_num=episode.index)
            for poster in tmdb_search:
                posters.append(poster.file_path)
    return posters

def get_tmdb_film_posters(var):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    tmdb = Movie()
    posters = []
    lib = config.filmslibrary.split(',')
    for l in lib:
        for film in plex.library.section(l.lstrip()).search(guid=var):
            logger.debug(film)
            print(film.title)
            g = str(film.guids)
            g = g[1:-1]
            g = re.sub(r'[*?:"<>| ]',"",g)
            g = re.sub("Guid","",g)
            g = g.split(",")
            f = filter(lambda a: "tmdb" in a, g)
            g = list(f)
            g = str(g[0])
            gv = [v for v in g if v.isnumeric()]
            g = "".join(gv)
            tmdb_search = tmdb.images(movie_id=g, include_image_language='en')
            for poster in tmdb_search.posters:
                posters.append(poster.file_path)
             
    return posters

def upload(request):   
    config = Plex.objects.get(pk=1)
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('data', ''))
            guid = data['guid']
            tmdb_poster = data['poster']    
            #logger.debug(data) 
            if 'movie' in guid:
                poster_size = (2000,3000)
                mediaType = 'film'
                film_lib = config.filmslibrary.split(',')
                for l in film_lib:
                    try:
                        movie, f = API.get_item(l, '', guid, mediaType)
                        if movie != None:
                            logger.info(f'Found the Film: {movie.title}')
                            t = re.sub('plex://movie/', '', guid)
                            def upload_cleanPoster():
                                tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                                film_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                                logger.debug('uploading poster')
                                process.upload(movie, film_poster)
                            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                            film_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                            img = Image.open(tmp_poster) 
                            img = img.resize(poster_size, Image.LANCZOS)
                            img.save(tmp_poster)
                            media_bak = os.path.join(settings.MEDIA_ROOT, mediaType+'/backup/'+t+'.png')
                            shutil.copy(film_poster, media_bak)                            
                            try:
                                r = film.objects.get(guid=guid)
                                hdr = r.hdr
                                audio = r.audio
                                resolution = r.res
                                if (hdr == None or audio==None or resolution==None):
                                    hdr = item.getHdr(f, None)
                                    filePath = item.sanitiseFilepath(f)
                                    hdr, audio = item.scanFile(f, filePath, film, hdr, movie.audio)
                                    process.dbUpdate(f, film, hdr, audio, mediaType)
                            except film.DoesNotExist: 
                                logger.debug('not in database')
                                filePath = item.sanitiseFilepath(f)
                                file_needs_scan = item.file_needs_scan(movie)
                                resolution = f.media[0].videoResolution
                                if file_needs_scan == True:
                                    logger.debug('scan required')
                                    hdr = item.getHdr(f, None)
                                    hdr, audio = item.scanFile(f, filePath, film, hdr, movie.audio)
                                    process.dbUpdate(f, film, hdr, audio, mediaType)
                                    
                                else:
                                    upload_cleanPoster() 
                            newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, media_bak, mediaType, t, film, poster_size)
                            process.bannerDecisions(f, resolution, resBanners ,hdr, hdrBanners, audio, audioBanners, t, tmp_poster, poster_size, 'film', film)
                            process.clear_old_posters()
                        jsondata = json.dumps({
                            'msg': render_to_string('app/messages.html', context={'message':'Success!', 'tag':'success'})
                        })
                        return HttpResponse(jsondata, content_type="application/json")
                    except Exception as e:
                        if 'TypeError' in repr(e):
                            pass
                        else:
                            logger.error("Film poster Error: "+repr(e))
                            pass
                        jsondata = json.dumps({
                        'msg': render_to_string('app/messages.html', context={'message':repr(e), 'tag':'error'})
                        })
                            
                        return HttpResponse(jsondata, content_type="application/json")                   
            if 'show' in guid:
                poster_size = (2000,3000)
                mediaType = 'show'
                audio = None
                db = show
                tv_lib = config.tvlibrary.split(',')
                for l in tv_lib:
                    try:
                        media, f = API.get_item(l, '', guid, mediaType)
                        if media != None:
                            logger.info(f'Found the Show: {media.title}')
                            t = re.sub('plex://show/', '', guid)
                            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                            media_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                            img = Image.open(tmp_poster) 
                            img = img.resize(poster_size, Image.LANCZOS)
                            img.save(tmp_poster)
                            media_bak = os.path.join(settings.MEDIA_ROOT, mediaType+'/backup/'+t+'.png')
                            shutil.copy(media_poster, media_bak)                            
                            hdr = media.hdr
                            resolution = media.resolution
                            process.dbUpdate(f, db, hdr, audio, mediaType)
                            if resolution != '4k' and hdr == False:
                                logger.debug('uploading poster')
                                process.upload(movie, film_poster)
                            else:
                                newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, media_bak, mediaType, t, db, poster_size)
                                process.bannerDecisions(f, resolution, resBanners ,hdr, hdrBanners, audio, audioBanners, t, tmp_poster, poster_size, mediaType, db)
                            process.clear_old_posters()
                        jsondata = json.dumps({
                            'msg': render_to_string('app/messages.html', context={'message':'Success!', 'tag':'success'})
                        })
                        return HttpResponse(jsondata, content_type="application/json") 
                    except Exception as e:
                        if 'TypeError' in repr(e):
                            pass
                        else:
                            logger.error("Film poster Error: "+repr(e))
                            pass
                        jsondata = json.dumps({
                        'msg': render_to_string('app/messages.html', context={'message':repr(e), 'tag':'error'})
                        })
            if 'season' in guid:
                poster_size = (2000,3000)
                mediaType = 'season'
                audio = None
                db = season
                tv_lib = config.tvlibrary.split(',')
                for l in tv_lib:
                    try:
                        media, f = API.get_item(l, '', guid, mediaType)
                        if media != None:
                            logger.info(f'Found the Show: {media.title}')
                            t = re.sub('plex://season/', '', guid)
                            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                            media_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                            img = Image.open(tmp_poster) 
                            img = img.resize(poster_size, Image.LANCZOS)
                            img.save(tmp_poster)
                            media_bak = os.path.join(settings.MEDIA_ROOT, mediaType+'/backup/'+t+'.png')
                            shutil.copy(media_poster, media_bak)                            
                            hdr = media.hdr
                            resolution = media.resolution
                            process.dbUpdate(f, db, hdr, audio, mediaType)
                            if resolution != '4k' and hdr == False:
                                item.savePoster(f, mediaType, t, media_poster, db)
                                logger.debug('uploading poster')
                                process.upload(movie, film_poster)
                            else:
                                newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, media_bak, mediaType, t, db, poster_size)
                                process.bannerDecisions(f, resolution, resBanners ,hdr, hdrBanners, audio, audioBanners, t, tmp_poster, poster_size, mediaType, db)
                            process.clear_old_posters()
                        jsondata = json.dumps({
                            'msg': render_to_string('app/messages.html', context={'message':'Success!', 'tag':'success'})
                        })
                        return HttpResponse(jsondata, content_type="application/json") 
                    except Exception as e:
                        if 'TypeError' in repr(e):
                            pass
                        else:
                            logger.error("Film poster Error: "+repr(e))
                            pass
                        jsondata = json.dumps({
                        'msg': render_to_string('app/messages.html', context={'message':repr(e), 'tag':'error'})
                        })
            if 'episode' in guid:
                poster_size = (1280,720)
                mediaType = 'episode'
                db = episode
                lib = config.tvlibrary.split(',')
                for l in lib:
                    try:
                        media, f = API.get_item(l, '', guid, mediaType)
                        if media != None:
                            logger.info(f'Found the Episode: {media.title}')
                            t = re.sub('plex://episode/', '', guid)
                            def upload_cleanPoster():
                                tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                                media_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                                logger.debug('uploading poster')
                                process.upload(media, media_poster)
                            tmp_poster = re.sub(' ','_', '/tmp/'+t+'_poster.png')
                            media_poster = tmdbPoster.getTmdbPoster(tmp_poster, tmdb_poster)
                            img = Image.open(tmp_poster) 
                            img = img.resize(poster_size, Image.LANCZOS)
                            img.save(tmp_poster)
                            media_bak = os.path.join(settings.MEDIA_ROOT, mediaType+'/backup/'+t+'.png')
                            shutil.copy(media_poster, media_bak)
                            try:
                                r = db.objects.get(guid=guid)
                                hdr = r.hdr
                                audio = r.audio
                                resolution = r.res
                                if (hdr == None or audio==None or resolution==None):
                                    hdr = item.getHdr(f, None)
                                    filePath = item.sanitiseFilepath(f)
                                    hdr, audio = item.scanFile(f, filePath, db, hdr, media.audio)
                                    process.dbUpdate(f, db, hdr, audio, mediaType)
                            except db.DoesNotExist: 
                                logger.debug('not in database')
                                filePath = item.sanitiseFilepath(f)
                                file_needs_scan = item.file_needs_scan(media)
                                resolution = f.media[0].videoResolution
                                if file_needs_scan == True:
                                    logger.debug('scan required')
                                    hdr = item.getHdr(f, None)
                                    hdr, audio = item.scanFile(f, filePath, db, hdr, media.audio)
                                    process.dbUpdate(f, db, hdr, audio, mediaType)
                                    
                                else:
                                    upload_cleanPoster()
                            newPoster, hdrBanners, audioBanners, resBanners = item.newPoster(f, media_bak, mediaType, t, db, poster_size)
                            banners.episodeBannerBackground(media_poster, size)
                            process.bannerDecisions(f, resolution, resBanners ,hdr, hdrBanners, audio, audioBanners, t, tmp_poster, poster_size, mediaType, db)
                            process.clear_old_posters()
                        jsondata = json.dumps({
                            'msg': render_to_string('app/messages.html', context={'message':'Success!', 'tag':'success'})
                        })
                        return HttpResponse(jsondata, content_type="application/json")
                    except Exception as e:
                        if 'TypeError' in repr(e):
                            pass
                        else:
                            logger.error("Film poster Error: "+repr(e))
                            pass
                        jsondata = json.dumps({
                        'msg': render_to_string('app/messages.html', context={'message':repr(e), 'tag':'error'})
                        })
                            
                        return HttpResponse(jsondata, content_type="application/json")     
        except Exception as e:
            jsondata = json.dumps({
                        'msg': render_to_string('app/messages.html', context={'message': repr(e), 'tag':'error'})
                    })
            return HttpResponse(jsondata, content_type="application/json")                         

def searchResults(request):
    if request.method == 'POST':
        libraries = item.libraries('film')
        tvlibraries = item.libraries('episode')
        r = json.dumps({
            'films': [],
            'shows': [],
            'seasons':[],
            'episodes': []
        })
        results = json.loads(r)
        query = request.POST.get("q")    
        print(query)
        for library in libraries:
            films= library.search(title=query)
            for f in films:
                fdb = film.objects.filter(guid=f.guid).first()
                try: fposter = fdb.poster
                except:
                    fposter = None
                films = {}
                films['title'] = f.title
                films['guid'] = f.guid
                films['thumbUrl'] = f.thumbUrl
                films['backup_poster'] = fposter
                results['films'].append(films)
        for tvlibrary in tvlibraries:
            ep = tvlibrary.search(title=query, libtype='episode')
            for ep in ep:
                epdb = episode.objects.filter(guid=ep.guid).first()
                try: eposter = epdb.poster
                except:
                    eposter = None
                episodes = {}
                episodes['title'] = ep.title
                episodes['guid'] = ep.guid
                episodes['thumbUrl'] = ep.thumbUrl
                episodes['backup_poster'] = eposter
                results['episodes'].append(episodes)
            seasons = tvlibrary.search(title=query, libtype='season')
            for s in seasons:               
                sdb = season.objects.filter(guid=s.guid).first()
                try: sposter = sdb.poster
                except:
                    sposter = None 
                seasons = {}
                seasons['title'] = s.title
                seasons['guid'] = s.guid
                seasons['thumbUrl'] = s.thumbUrl
                seasons['backup_poster'] = sposter
                results['seasons'].append(seasons)
            shows = tvlibrary.search(title=query, libtype='show')
            for sh in shows:
                shdb = show.objects.filter(guid=sh.guid).first()
                try: shposter = shdb.poster
                except:
                    shposter = None 
                shows = {}
                shows['title'] = sh.title
                shows['guid'] = sh.guid
                shows['thumbUrl'] = sh.thumbUrl
                shows['backup_poster'] = shposter
                results['shows'].append(shows)
        context = {
            'pagetitle': 'search', 
            'results': results,
            'version': version
        }
        return render(request, 'app/results.html', context)
    context = {
            'pagetitle': 'search',  
            'version': version
        }    
    return render(request, 'app/results.html', context)

@csrf_exempt
def spoiler_webhook(request):
    try:
        if request.method == 'POST':
            data = request.POST
            d = json.loads(data['payload'])
            user = d['Account']['id']
            guid = d['Metadata']['guid']
            print(d['event'])
            if d['event'] == 'media.scrobble' and d['user'] == True:
               blurSpoilers.delay(guid)
            else:
                print("user is not server owner")
    except Exception as e:
        print(repr(e))
    return HttpResponse()

def updateTasks(request):
    tasks = PeriodicTask.objects.all()
    jsontask = json.loads(json.dumps({'tasks': []}))
    for task in tasks:
        t = {}
        t['name'] = task.name
        t['id'] = task.id
        t['enabled'] = task.enabled
        jsontask['tasks'].append(t)
    data = json.dumps(jsontask)
    print(data)

    response = HttpResponse(data, content_type="application/json")
    response.status_code = 200
    return response


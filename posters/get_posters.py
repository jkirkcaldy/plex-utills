from posters.models import *
from utils.models import Plex
from posters.utils import banners, item, process, tmdbPoster, file
from django.conf import settings
import re, os, cv2
from PIL import Image
from tmdbv3api import TMDb, Search, Movie, Discover, Season, Episode, TV

cutoff = 10
import logging

logger = logging.getLogger(__name__)

config, advancedConfig = item.getConfig()
plex = item.getPlex()

def get_tmdb_film_posters(var, mediaType, season, episode):
    libraries = item.libraries(mediaType)
    posters = []
    for library in libraries:
        def getG(g):
            g = g[1:-1]
            g = re.sub(r'[*?:"<>| ]',"",g)
            g = re.sub("Guid","",g)
            g = g.split(",")
            f = filter(lambda a: "tmdb" in a, g)
            g = list(f)
            g = str(g[0])
            gv = [v for v in g if v.isnumeric()]
            g = "".join(gv)
        if mediaType == 'episode':
            tmdb = Episode()
            for i in library.search(guid=var, libtype=mediaType):
                for show in library.search(libtype='show', guid=i.grandparentGuid):
                    g = str(show.guids)
                    g = getG(g)
                    tmdb_search = tmdb.images(tv_id=g, season_num = season, epiosde_num=episode, include_image_language='en')
        if mediaType == 'season':
            tmdb = Season()
            for s in library.search(guid=var, libtype=mediaType):
                for show in library.search(libtype='show', guid=s.parentGuid):
                    g = str(show.guids)
                    g = getG(g)
                    tmdb_search = tmdb.images(tv_id=g, season_num=season, include_image_language='en')
        if mediaType == 'show':
            tmdb = TV()
            for i in library.search(guid=var, libtype=mediaType):
                g = str(i.guids)
                g = getG(g)
                tmdb_search = tmdb.images(tv_id=g, include_image_language='en')
        if mediaType == 'film':
            tmdb = Movie()
            for i in library.search(guid=var):
                g = str(i.guids)
                g = getG(g)
                tmdb_search = tmdb.images(movie_id=g, include_image_language='en')

        for poster in tmdb_search.posters:
            posters.append(poster.file_path)
    return posters
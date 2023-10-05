from django.db.models import Q
from django.shortcuts import render, redirect
from plexapi.server import PlexServer
from django.http import HttpResponse
import os
import re
import requests
import shutil 
from pathlib import PureWindowsPath, PurePosixPath
import logging

from posters import classes
from posters.models import *
from posters.utils import *

logger = logging.getLogger(__name__)

config, advancedConfig = item.getConfig()
plex = item.getPlex()
def get_version():
    with open('./version') as f: s = f.read()
    return s
version = get_version()





def help(request):

    file_paths = './app/static/img/tmp/'
    for root, dirs, files in os.walk(file_paths):
        for f in files:
            if f.endswith('.png'):# and 'poster_not_found' not in f):
                print(f)
                os.remove(file_paths+f)   
    try:
        os.remove("app/support.zip")
        os.remove('./app/static/img/poster.png')
        os.remove('./app/static/img/poster_bak.png')
    except FileNotFoundError as e:
        pass
        
    mpath = [f for f in os.listdir('/films') if not f.startswith('.')]
    try:
        libraries = item.libraries('film') 
    except requests.exceptions.ConnectionError as e:
        logger.error(repr(e))
        message = "Can not connect to your plex server, please check your config"
        context = {
            'pagetitle': 'Error',
            'pageheading': 'Connection Error',
            'error': e,
            'message': message,
            'version': version,
        }
        return render('error.html', context), 500

    advanced_filter = {
        'or': [
            {'resolution': '4k'},
            {'hdr': True}
        ]
    }
    for library in libraries:
        for i in library.search(sort='random', limit='1', filters=advanced_filter):
            p = item.poster(i, 'static/img/tmp/help_poster.png', (200,300))
            f_item = film.objects.filter(guid=i.guid).first()
            backup_poster = f_item.poster
            current_poster = 'static/img/tmp/current_poster.png'
            logger.debug('Running help script')
            plex_filepath = i.media[0].parts[0].file
            filmtitle = i.title
            try:
                p = PureWindowsPath(i.media[0].parts[0].file)
                p1 = re.findall('[A-Z]', p.parts[0])
                if p1 != []:
                    logger.debug(p1)
                    newdir = PurePosixPath('/films', *p.parts[1:])
                    logger.debug(newdir)
                elif config[0].manualplexpath == 1:
                    newdir = re.sub(config[0].manualplexpathfield, '/films', i.media[0].parts[0].file)
                else:
                    newdir = re.sub(config[0].plexpath, '/films', i.media[0].parts[0].file)
            except:
                newdir = 'Can not be converted'
            logger.debug(newdir)
            if os.path.exists(newdir) == True:
                exists = 'True'
                logger.debug("PATH EXISTS")
            else:
                exists = 'False'
                logger.debug("PATH DOES NOT EXIST")
            context = {
                'exists': exists, 
                'pagetitle': 'Help',
                'plex': config, 
                'plex_filepath': plex_filepath, 
                'filmtitle': filmtitle, 
                'newdir': newdir, 
                'mpath': mpath, 
                'backup_poster': backup_poster, 
                'current_poster': current_poster, 
                'pageheadding': 'Help', 
                'version': version
            }
    return render(request, 'app/help.html', context)


def get_item(library, title, guid, mediaType):
    plex = item.getPlex()
    library = plex.library.section(library)
    if mediaType == 'film':
        key = [film.key for film in library.search(title=title, guid=guid, sort='titleSort:desc')]
        n = len(key)
        for x in range(n):
            for f  in plex.fetchItems(key[x]):
                logger.debug(f.title)
                audio = ''
                try:
                    if 'Atmos' in f.media[0].parts[0].streams[1].extendedDisplayTitle:
                        audio = 'Dolby Atmos'

                    if (f.media[0].parts[0].streams[1].title and 'DTS:X' in f.media[0].parts[0].streams[1].title):
                                audio = 'DTS:X'
                except: pass
                else:
                    audio = f.media[0].parts[0].streams[1].displayTitle

                film = classes.film_processing(f.title, f.guid, f.guids, f.media[0].parts[0].size, f.media[0].videoResolution, f.media[0].parts[0].streams[0].extendedDisplayTitle, audio, f.media[0].parts[0].file)
                return film, f
    elif mediaType == 'show' or mediaType == 'season':
        key = [film.key for film in library.search(title=title, guid=guid, sort='titleSort:desc', libtype=mediaType)]
        n = len(key)
        for x in range(n):
            for f  in plex.fetchItems(key[x]):
                logger.debug(f.title)
                audio = ''
                if mediaType == 'show':
                    ephdr = library.search(libtype='episode', hdr=True, filters={'show.guid':guid})
                    epres = library.search(libtype='episode', resolution='4k', filters={'show.guid':guid})
                elif mediaType == 'season':
                    ephdr = library.search(libtype='episode', hdr=True, filters={'season.guid':guid})
                    epres = library.search(libtype='episode', resolution='4k', filters={'season.guid':guid})
                if len(ephdr) >= 1:
                    hdr=True
                else:
                    hdr=False
                if len(epres) >= 1:
                    res='4k'
                else:
                    res='1080'
                logger.debug(res)
                show = classes.show_processing(f.title, f.guid, f.guids, res, hdr)
                return show, f  
    if mediaType == 'episode':
        key = [film.key for film in library.search(title=title, libtype=mediaType, guid=guid, sort='titleSort:desc')]
        n = len(key)
        for x in range(n):
            for f  in plex.fetchItems(key[x]):
                print(f.title)
                audio = ''
                try:
                    if 'Atmos' in f.media[0].parts[0].streams[1].extendedDisplayTitle:
                        audio = 'Dolby Atmos'

                    if (f.media[0].parts[0].streams[1].title and 'DTS:X' in f.media[0].parts[0].streams[1].title):
                                audio = 'DTS:X'
                except: pass
                else:
                    audio = f.media[0].parts[0].streams[1].displayTitle

                episode = classes.film_processing(f.title, f.guid, f.guids, f.media[0].parts[0].size, f.media[0].videoResolution, f.media[0].parts[0].streams[0].extendedDisplayTitle, audio, f.media[0].parts[0].file)
                return episode, f
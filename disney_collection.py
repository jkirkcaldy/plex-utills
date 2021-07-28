#!/usr/bin/env python3
from collections import defaultdict
from plexapi.server import PlexServer
from configparser import ConfigParser
from datetime import datetime
#Read config.ini file
config_object = ConfigParser()
config_object.read("/config/config.ini")
server = config_object["PLEXSERVER"]

baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
movies_section = plex.library.section(films)
added = movies_section.search(sort='titleSort')

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

print(current_time, ": Disney Collection script starting now")

for movie in added:
    try:
        if "Disney" in movie.studio:
            movie.addCollection('Disney')
            print('%s (%s)' % (movie.title, movie.studio))
    # Skip movie if there is no studio info
    except TypeError:
        continue

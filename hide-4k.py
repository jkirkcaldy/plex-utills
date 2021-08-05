#!/usr/local/bin/python
from collections import defaultdict
from plexapi.server import PlexServer
from datetime import datetime
from configparser import ConfigParser
import socket

#Read config.ini file
config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
optimise = str.lower((server["transcode"]))
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": Hide 4k films script starting now")

baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
movies_section = plex.library.section(films)
added = movies_section.search(resolution='4k', sort='addedAt')
b = movies_section.search(label='untranscodable', sort='addedAt')

for movie in added:
    resolutions = {m.videoResolution for m in movie.media}
    if len(resolutions) < 2 and '4k' in resolutions:
        if optimise == 'False':
            movie.addLabel('Untranscodable')   
            print(movie.title+' has only 4k avaialble, setting untranscodable' )
        elif optimise == 'true':
            print('Sending', movie.title, 'to be transcoded')
            movie.optimize(deviceProfile="Android", videoQuality=10)
for movie in b:
    resolutions = {m.videoResolution for m in movie.media}
    if len(resolutions) > 1 and '4k' in resolutions:
        movie.removeLabel('Untranscodable')

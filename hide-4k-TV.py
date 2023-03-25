#!/usr/local/bin/python
from collections import defaultdict
from plexapi.server import PlexServer
from datetime import datetime
import socket

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": Hide 4k TV episodes script starting now")

baseurl = "XXXXXX"
token = "XXXXXXX"
shows = "TV Show Library name"
plex = PlexServer(baseurl, token)
tv_section = plex.library.section(shows)
added = tv_section.search(sort='titleSort')

# iterate through the shows
ii = 1
jj = 0
kk = 0
for show in added:
#   get episodes
    print('Checking Show '+str(ii)+' of '+str(len(added)), end = "\r")
    episodes = show.episodes()
    untranscodable = 0
#   iterate through episodes
    for episode in episodes:
        resolutions = {e.videoResolution for e in episode.media}
#       check if episode only has a 4k version, if so increment "untranscodable" by 1
        if len(resolutions) < 2 and '4k' in resolutions:
            untranscodable += 1
    if untranscodable == 0 and "Untranscodable" in str(show.labels):
        show.removeLabel('Untranscodable')
        print('REMOVING LABEL: '+show.title+' now has '+str(untranscodable)+' untranscodable episodes,  removing Untranscodable label' )
        kk += 1
    elif untranscodable == 0 and "Untranscodable" not in str(show.labels):
        kk += 1
    elif untranscodable > 0 and untranscodable == len(episodes):
        show.addLabel('Untranscodable')
        print('ENTIRE SHOW: '+show.title+' has '+str(untranscodable)+'/'+str(len(episodes))+' untranscodable episodes, adding Unstranscodable la$
        jj += 1
    elif untranscodable > 0 and untranscodable < len(episodes):
        show.addLabel('Untranscodable')
        print('PARTIAL SHOW: '+show.title+' has '+str(untranscodable)+'/'+str(len(episodes))+' untranscodable episodes, adding Unstranscodable l$
        jj +=1
    ii += 1
print('All shows checked '+str(kk)+' are transcodable, '+str(jj)+' are untranscodable')

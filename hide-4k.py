#!/usr/bin/env python3

from collections import defaultdict
from plexapi.server import PlexServer

from configparser import ConfigParser

#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

server = config_object["PLEXSERVER"]


def to_tags(labels):
    return [l.tag for l in labels]



if __name__ == "__main__":
    baseurl = (server["PLEX_URL"])
    token = (server["TOKEN"])
    films = (server["FILMSLIBRARY"])
    plex = PlexServer(baseurl, token)
    movies_section = plex.library.section(films)
    movies = defaultdict(list)
    added = movies_section.search(sort='titleSort')

    #print(added)

    for movie in added:
        resolutions = {m.videoResolution for m in movie.media}
        if len(resolutions) < 2 and '4k' in resolutions:
            movie.addLabel('Untranscodable')   
            print(movie)
        if len(resolutions) > 1 and '4k' in resolutions:
            movie.removeLabel('Untranscodable')
            print(movie)             

                    

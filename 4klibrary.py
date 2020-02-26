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
    movies_section = plex.library.section('films')
    movies = defaultdict(list)
    added = movies_section.search(sort='addedAt:desc')

    for movie in added:
        resolutions = {m.videoResolution for m in movie.media}
        if len(resolutions) > 1 and '4k' in resolutions:
            movie.addCollection(movie.title)
            movie.split()


    added = movies_section.search(sort='addedAt:desc')
    for movie in added:
        movies[movie.title].append(movie)

    for title, entries in movies.items():
        # add Transcodable
        for entry in entries:
            if 'Transcodable' not in to_tags(entry.labels) and entry.media[0].videoResolution != '4k':
                entry.addLabel('Transcodable')
            if 'Transcodable' in to_tags(entry.labels) and entry.media[0].videoResolution == '4k':
                entry.removeLabel('Transcodable')
        # find the best
        existing_bests = [e for e in entries if 'Best' in to_tags(e.labels)]
        uhd_version = next((e for e in entries if e.media[0].videoResolution == '4k'), None)
        # assume uhd version is the best if there is one, otherwise use bitrate
        if uhd_version is not None:
            best = uhd_version
        else:
            best = sorted(entries, key=lambda e: e.media[0].bitrate, reverse=True)[0]
        if len(existing_bests) != 1 or existing_bests[0] != best:
            for e in existing_bests:
                e.removeLabel('Best')
            best.addLabel('Best')

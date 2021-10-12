
from plexapi.server import PlexServer
import logging

import sqlite3

logger = logging.getLogger('4K-posters')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def pixar():

    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    movies_section = plex.library.section(config[0][3])
    added = movies_section.search(sort='titleSort')

    logger.info("Pixar Collection script starting now")

    for movie in added:
        try:
            if "Pixar" in movie.studio:
                movie.addCollection('Pixar')
                logger.info(movie.title, movie.studio)
        # Skip movie if there is no studio info
        except TypeError:
            continue

def disney():

    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()

    plex = PlexServer(config[0][1], config[0][2])
    movies_section = plex.library.section(config[0][3])
    added = movies_section.search(sort='titleSort')

    logger.info("Pixar Collection script starting now")

    for movie in added:
        try:
            if "Disney" in movie.studio:
                movie.addCollection('Pixar')
                logger.info(movie.title, movie.studio)
        # Skip movie if there is no studio info
        except TypeError:
            continue

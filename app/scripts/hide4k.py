#!/usr/local/bin/python
from plexapi.server import PlexServer
import logging
import sqlite3


logger = logging.getLogger('Hide-4K-Films')
logger.setLevel(logging.INFO)
handler = logging.FileHandler("./app/logs/log.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def hide4k():
    conn = sqlite3.connect('./app/app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plex_utills")
    config = c.fetchall()
    plex = PlexServer(config[0][1], config[0][2])
    films = plex.library.section(config[0][3])


    logger.info("Hide 4k films script starting now")

    #movies_section = plex.library.section(films)
    added = films.search(resolution='4k', sort='addedAt')
    b = films.search(label='untranscodable', sort='addedAt')

    for movie in added:
        resolutions = {m.videoResolution for m in movie.media}
        if len(resolutions) < 2 and '4k' in resolutions:
            if config[0][21] == 0:
                movie.addLabel('Untranscodable')   
                logger.info(movie.title+' has only 4k avaialble, setting untranscodable' )
            elif config[0][21] == 1:
                logger.info('Sending '+ movie.title+ ' to be transcoded')
                movie.optimize(deviceProfile="Android", videoQuality=10)
        else:
            logger.info('No more films found, moving on.')
    for movie in b:
        resolutions = {m.videoResolution for m in movie.media}
        if len(resolutions) > 1 and '4k' in resolutions:
            movie.removeLabel('Untranscodable')
            logger.info(movie.title+ ' removing untranscodable label')
        else:
            logger.info('No more films found, moving on.')    

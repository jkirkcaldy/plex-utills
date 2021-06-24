<<<<<<< Updated upstream
#!/usr/bin/env python3
import fnmatch
from collections import defaultdict
from plexapi.server import PlexServer

from configparser import ConfigParser

#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

server = config_object["PLEXSERVER"]


baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
movies_section = plex.library.section('films')
movies = defaultdict(list)
added = movies_section.search(sort='titleSort')



for movie in added:
    movies[movie.title].append(movie.studio)
    #print(movies)      
    #studio = {movie.studio for movie in movies}
    #fnmatch.filter(movies, '[*]Disney[*]')
    #print(movies)
    fnmatch.filter(movies, '*Disney*')
print('%s (%s)' % (movie.title, movie.studio))

    
=======
from pathlib import Path
from PIL import Image
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
import stat
from configparser import ConfigParser
import platform
import imagehash

config_object = ConfigParser()
config_object.read("config.ini")
server = config_object["PLEXSERVER"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
plexlibrary = (server["FILMSLIBRARY"])
ppath = (server["PLEXPATH"])
mpath = (server["MOUNTEDPATH"])
pbak = (server["POSTER_BU"])
plex = PlexServer(baseurl, token)
films = plex.library.section(plexlibrary)
banner_4k = Image.open("4K-Template.png")
banner_hdr = Image.open("hdr-poster.png")
banner_4k_hdr = Image.open("4k-hdr-poster.png")
chk_banner = Image.open("chk-4k.png")
chk_hdr = Image.open("chk_hdr.png")
size = (911,1367)
box= (0,0,911,100)
hdr_box = (0,611,215,720)

for i in films.search():
    print(i.title + ' 4k HDR')    
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'  
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"
    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)

#   print('creating poster')    
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    backgroundchk = background.crop(hdr_box)
    background.save("test.png")
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_hdr)
    cutoff= 5
    if hash0 - hash1 < cutoff:
        print('images are similar')
    else:
        background.paste(banner_hdr, (0, 0), banner_hdr)
        background.save('poster.png')
    

    
#   i.uploadPoster(filepath="poster.png")
#   os.remove('poster.png')     
>>>>>>> Stashed changes

from pathlib import Path
from PIL import Image
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re

baseurl = ''
token = ''
plex = PlexServer(baseurl, token)

films = plex.library.section('Films')
banner_4k = Image.open("4K-Template.png")
banner_hdr = Image.open("hdr-poster.png")
banner_4k_hdr = Image.open("4k-hdr-poster.png")
size = (911,1367)

def poster_4k_hdr():
    print(i.title)
    imgurl = baseurl + i.thumb + '.png'
    img = requests.get(imgurl, stream=True)
    filename = "poster"
    png = os.path.splitext(filename)[0]+'.png'
    if img.status_code == 200:
        img.raw.decode_content = True
        with open(png, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
    
    background = Image.open(png)
    background = background.resize(size,Image.ANTIALIAS)
    background.paste(banner_4k_hdr, (0, 0), banner_4k_hdr)
    background.save(png)
    i.uploadPoster(filepath="poster.png")
    os.remove(png) 



def poster_4k():
    print(i.title)
    imgurl = baseurl + i.thumb + '.png'
    img = requests.get(imgurl, stream=True)
    filename = "poster"
    png = os.path.splitext(filename)[0]+'.png'
    if img.status_code == 200:
        img.raw.decode_content = True
        with open(png, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
    
    background = Image.open(png)
    background = background.resize(size,Image.ANTIALIAS)
    background.paste(banner_4k, (0, 0), banner_4k)
    background.save(png)
    i.uploadPoster(filepath="poster.png")
    os.remove(png) 
def poster_hdr():
    print(i.title)
    imgurl = baseurl + i.thumb + '.png'
    img = requests.get(imgurl, stream=True)
    filename = "poster"
    png = os.path.splitext(filename)[0]+'.png'
    if img.status_code == 200:
        img.raw.decode_content = True
        with open(png, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
    
    background = Image.open(png)
    background = background.resize(size,Image.ANTIALIAS)
    background.paste(banner_hdr, (0, 0), banner_hdr)
    background.save(png)
    i.uploadPoster(filepath="poster.png")
    os.remove(png) 

for i in films.search(resolution="4k", hdr=True):
    poster_4k_hdr()
for i in films.search(resolution="4k", hdr=False):
    poster_4k()
for i in films.search(resolution="1080,720", hdr=True):
    poster_hdr()

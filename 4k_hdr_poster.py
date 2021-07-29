#!/usr/local/bin/python
from pathlib import Path
from PIL import Image, ImageChops
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
from colorama import Fore, Back, Style
from requests.api import get
from requests.models import REDIRECT_STATI
from datetime import datetime

# Do not edit these, use the config file to make any changes

config_object = ConfigParser()
config_object.read("/config/config.ini")
server = config_object["PLEXSERVER"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
plexlibrary = (server["FILMSLIBRARY"])
ppath = (server["PLEXPATH"])
mpath = (server["MOUNTEDPATH"])
pbak = (server["POSTER_BU"])
HDR_BANNER = (server["HDR_BANNER"])
plex = PlexServer(baseurl, token)
films = plex.library.section(plexlibrary)
banner_4k = Image.open("img/4K-Template.png")
banner_hdr = Image.open("img/hdr-poster.png")
chk_banner = Image.open("img/chk-4k.png")
chk_hdr = Image.open("img/chk_hdr.png")
size = (911,1367)
box= (0,0,911,100)
hdr_box = (0,611,215,720)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": 4k HDR poster script starting now.")          

def add_banner():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    backgroundchk = background.crop(box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_banner)
    cutoff= 5
    if hash0 - hash1 < cutoff:
        print('4K banner exists, moving on...')
    else:
        background.paste(banner_4k, (0, 0), banner_4k)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")

    
def add_hdr():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    backgroundchk = background.crop(hdr_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_hdr)
    cutoff= 5
    if hash0 - hash1 < cutoff:
        print('HDR banner exists, moving on...')
    else:
        background.paste(banner_hdr, (0, 0), banner_hdr)
        background.save('poster.png')
        i.uploadPoster(filepath="poster.png")

def get_poster():
    backup = Path(ppath).joinpath(mpath, i.media[0].parts[0].file).parent.joinpath('poster_bak.png')
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = Path("poster.png")

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(str(filename), 'wb') as f:
            shutil.copyfileobj(img.raw, f)
        if pbak == 'True': 
            if backup.exists(): 
                print('Backup File Exists, Skipping...')
            else:        
                print('Creating a backup file')
                dest = shutil.copyfile(str(filename), str(backup))
    else:
        print(Fore.RED+films.title+"cannot find the poster for this film")
        print(Fore.RESET)


def poster_4k_hdr():
    print(i.title + ' 4k HDR')     
    get_poster()
    add_banner() 
    add_hdr()                                  
    os.remove('poster.png')              


def poster_4k():   
    print(i.title + " 4K Poster")
    get_poster()
    add_banner()                                  
    os.remove('poster.png')   


                   
def poster_hdr():
    print(i.title + " HDR Poster") 
    get_poster() 
    add_hdr()                                  
    os.remove('poster.png')              

if HDR_BANNER == 'True':
    for i in films.search(resolution="4k", hdr=False):
        try:
            poster_4k()
        except FileNotFoundError:
            print(Fore.RED+films.title+" Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue    
    for i in films.search(resolution="4k", hdr=True):
        try:
            poster_4k_hdr()
        except FileNotFoundError:
            print(Fore.RED+films.title+" Error, the 4k HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
    for i in films.search(resolution="1080,720", hdr=True):
        try:
            poster_hdr()
        except FileNotFoundError:
            print(Fore.RED+films.title+" Error, the HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
else:
    print('Creating 4k posters only')
    for i in films.search(resolution="4k"):
        try:
            poster_4k()
        except FileNotFoundError:
            print(Fore.RED+films.title+" Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue

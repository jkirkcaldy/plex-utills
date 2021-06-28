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

# Do not edit these, use the config file to make any changes

config_object = ConfigParser()
config_object.read("config.ini")
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
 

def poster_4k_hdr():
    print(i.title + ' 4k HDR')    
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')   
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)

    if pbak == 'True': 
        if backup == True: 
            print('Backup File Exists, Skipping...')
            add_banner() 
            add_hdr()                                  
        else:
            print('Creating a backup file')
            dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            add_banner()
            add_hdr()
    else:
        add_banner()
        add_hdr()
    os.remove('poster.png')              


def poster_4k():   
    print(i.title + " 4K Poster")
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')  
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)

    if pbak == 'True': 
        if backup == True: 
            print('Backup File Exists, Skipping...')
            add_banner()                                   
        else:
            print('Creating a backup file')
            dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            add_banner()
    else:
        add_banner()
    os.remove('poster.png')   


                   
def poster_hdr():
    print(i.title + " HDR Poster")
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')  
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)

    if pbak == 'True': 
        if backup == True: 
            print('Backup File Exists, Skipping...')
            add_hdr()                                   
        else:
            print('Creating a backup file')
            dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            add_hdr()
    else:
        add_hdr()
    os.remove('poster.png')              

if HDR_BANNER == 'True':
    for i in films.search(resolution="4k", hdr=False):
        try:
            poster_4k()
        except TypeError:
            print(Fore.RED+films.title+" Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue    
    for i in films.search(resolution="4k", hdr=True):
        try:
            poster_4k_hdr()
        except TypeError:
            print(Fore.RED+films.title+" Error, the 4k HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
    for i in films.search(resolution="1080,720", hdr=True):
        try:
            poster_hdr()
        except TypeError:
            print(Fore.RED+films.title+" Error, the HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
else:
    print('Creating 4k posters only')
    for i in films.search(resolution="4k"):
        try:
            poster_4k()
        except TypeError:
            print(Fore.RED+films.title+" Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue

#!/usr/local/bin/python3
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
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
options = config_object["OPTIONS"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
plex = PlexServer(baseurl, token)
plexlibrary = (server["FILMSLIBRARY"])
films = plex.library.section(plexlibrary)
ppath = (server["PLEXPATH"])
mpath = (server["MOUNTEDPATH"])

pbak = str.lower((options["POSTER_BU"]))
HDR_BANNER = str.lower((options["HDR_BANNER"]))
mini_4k = str.lower((options["mini_4k"]))

banner_4k = Image.open("img/4K-Template.png")
mini_4k_banner = Image.open("img/4K-mini-Template.png")
banner_hdr = Image.open("img/hdr-poster.png")
chk_banner = Image.open("img/chk-4k.png")
chk_mini_banner = Image.open("img/chk-mini-4k2.png")
chk_hdr = Image.open("img/chk_hdr.png")
size = (911,1367)
box= (0,0,911,100)
mini_box = (0,0,150,125)
hdr_box = (0,611,215,720)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": 4k HDR poster script starting now.")          

def check_for_mini():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    backgroundchk = background.crop(mini_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_mini_banner)
    cutoff= 10
    if hash0 - hash1 < cutoff:
        print(Fore.LIGHTMAGENTA_EX, 'Mini 4K banner exists, moving on...',Fore.RESET)
    else:    
        if mini_4k == 'true':
            add_mini_banner()
        else:
            add_banner()     
        
        

def check_for_banner():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    backgroundchk = background.crop(box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_banner)
    cutoff= 5
    if hash0 - hash1 < cutoff:
        print(Fore.LIGHTMAGENTA_EX, '4K banner exists, moving on...', Fore.RESET)
    else:
        check_for_mini()     

def add_banner():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    background.paste(banner_4k, (0, 0), banner_4k)
    background.save('poster.png')
    i.uploadPoster(filepath="poster.png")

def add_mini_banner():
    background = Image.open('poster.png')
    background = background.resize(size,Image.ANTIALIAS)
    background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
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
    newdir = os.path.dirname(re.sub(ppath, mpath, i.media[0].parts[0].file))+'/'
    backup = os.path.exists(newdir+'poster_bak.png')
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = "poster.png"

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
        if pbak == 'true': 
            if backup == True: 
                #open backup poster to compare it to the current poster. If it is similar enough it will skip, if it's changed then create a new backup and add the banner. 
                poster = os.path.join(newdir, 'poster_bak.png')
                b_check1 = Image.open(filename)
                b_check = Image.open(poster)
                b_hash = imagehash.average_hash(b_check)
                b_hash1 = imagehash.average_hash(b_check1)
                cutoff = 10
                if b_hash - b_hash1 < cutoff:    
                    print(Fore.GREEN, 'Backup File Exists, Skipping...', Fore.RESET)
                else:
                    
                    #Check to see if the poster has a 4k Banner
                    background = Image.open(filename)
                    background = background.resize(size,Image.ANTIALIAS)
                    backgroundchk = background.crop(box)
                    hash0 = imagehash.average_hash(backgroundchk)
                    hash1 = imagehash.average_hash(chk_banner)
                    cutoff= 5
                    if hash0 - hash1 < cutoff:
                        print(Fore.LIGHTRED_EX, 'Poster has 4k banner, skipping backup', Fore.RESET)
                    else:
                        #Check if the poster has a mini 4k banner
                        background = Image.open(filename)
                        background = background.resize(size,Image.ANTIALIAS)
                        backgroundchk = background.crop(mini_box)
                        hash0 = imagehash.average_hash(backgroundchk)
                        hash1 = imagehash.average_hash(chk_mini_banner)
                        cutoff= 10
                        if hash0 - hash1 < cutoff: 
                            print(Fore.LIGHTRED_EX, 'Poster has mini 4K banner, skipping backup', Fore.RESET)
                        else:
                            print(Fore.MAGENTA, 'New poster detected, Creating a new backup', Fore.RESET)  
                            os.remove(poster)
                            print(Fore.CYAN, 'Check Passed, Creating a backup file', Fore.RESET)
                            dest = shutil.copyfile(filename, newdir+'poster_bak.png')
            else:        
                print(Fore.BLUE, 'Creating a backup file', Fore.RESET)
                dest = shutil.copyfile(filename, newdir+'poster_bak.png')

    else:
        print(Fore.RED+films.title+"cannot find the poster for this film")
        print(Fore.RESET)

def poster_4k_hdr():
    print(i.title + ' 4k HDR')     
    get_poster()
    check_for_banner() 
    add_hdr()                                  
    os.remove('poster.png')              

def poster_4k():   
    print(i.title + " 4K Poster")
    get_poster()
    check_for_banner()                             
    os.remove('poster.png')   
                  
def poster_hdr():
    print(i.title + " HDR Poster") 
    get_poster() 
    add_hdr()                                  
    os.remove('poster.png')              


if HDR_BANNER == 'true':
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

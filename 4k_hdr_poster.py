#!/usr/local/bin/python3
from pathlib import Path
from PIL import Image
import requests
import shutil
import os
import imagehash
from colorama import Fore
from datetime import datetime
from readConfig import config
import tempfile

tempfilename = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name

# Get the config
conf = config()

banner_4k = Image.open("img/4K-Template.png")
mini_4k_banner = Image.open("img/4K-mini-Template.png")
banner_hdr = Image.open("img/hdr-poster.png")
mini_4k_banner = Image.open("img/4K-mini-Template.png")

chk_banner = Image.open("img/chk-4k.png")
chk_mini_banner = Image.open("img/chk-mini-4k.png")
chk_hdr = Image.open("img/chk_hdr.png")
chk_mini_banner = Image.open("img/chk-mini-4k.png")

size = (911, 1367)
box = (0, 0, 911, 100)
hdr_box = (0, 611, 215, 720)
mini_box = (0, 0, 301, 268)

size = (911, 1367)
box = (0, 0, 911, 100)
mini_box = (0, 0, 301, 268)
hdr_box = (0, 611, 215, 720)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print(current_time, ": 4k HDR poster script starting now.")


def add_mini_banner():
    background = Image.open(tempfilename)
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(mini_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_mini_banner)
    cutoff = 15
    if hash0 - hash1 < cutoff:
        print('4K banner exists, moving on...')
    else:
        background.paste(mini_4k_banner, (0, 0), mini_4k_banner)
        background.save(tempfilename)
        i.uploadPoster(filepath=tempfilename)


def add_banner():
    background = Image.open(tempfilename)
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_banner)
    cutoff = 5
    if hash0 - hash1 < cutoff:
        print('4K banner exists, moving on...')
    else:
        background.paste(banner_4k, (0, 0), banner_4k)
        background.save(tempfilename)
        i.uploadPoster(filepath=tempfilename)


def add_hdr():
    background = Image.open(tempfilename)
    background = background.resize(size, Image.ANTIALIAS)
    backgroundchk = background.crop(hdr_box)
    hash0 = imagehash.average_hash(backgroundchk)
    hash1 = imagehash.average_hash(chk_hdr)
    cutoff = 5
    if hash0 - hash1 < cutoff:
        print('HDR banner exists, moving on...')
    else:
        background.paste(banner_hdr, (0, 0), banner_hdr)
        background.save(tempfilename)
        i.uploadPoster(filepath=tempfilename)


def get_poster():
    backup = conf.LIBRARY_PATH.joinpath(
        i.media[0].parts[0].file).parent.joinpath('poster_bak.png')
    imgurl = i.posterUrl
    img = requests.get(imgurl, stream=True)
    filename = Path(tempfilename)

    if img.status_code == 200:
        img.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(img.raw, f)
        if conf.POSTER_BU:
            if conf.createFoldersIfMissing:
                backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                print('Backup File Exists, Skipping...')
            else:
                print('Creating a backup file')
                dest = shutil.copyfile(filename, newdir+'poster_bak.png')
    else:
        print(Fore.RED+conf.films.title+" cannot find the poster for this film")
        print(Fore.RESET)


def poster_4k_hdr():
    print(i.title + ' 4k HDR')
    get_poster()
    if conf.mini_4k:
        add_mini_banner()
    else:
        add_banner()
    add_hdr()
    os.remove(tempfilename)


def poster_4k():
    print(i.title + " 4K Poster")
    get_poster()
    add_banner()
    os.remove(tempfilename)


def poster_hdr():
    print(i.title + " HDR Poster")
    get_poster()
    add_hdr()
    os.remove(tempfilename)


if conf.HDR_BANNER:
    for i in conf.films.search(resolution="4k", hdr=False):
        try:
            poster_4k()
        except FileNotFoundError:
            print(Fore.RED+conf.films.title +
                  " Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue
    for i in conf.films.search(resolution="4k", hdr=True):
        try:
            poster_4k_hdr()
        except FileNotFoundError:
            print(Fore.RED+conf.films.title +
                  " Error, the 4k HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
    for i in conf.films.search(resolution="1080,720", hdr=True):
        try:
            poster_hdr()
        except FileNotFoundError:
            print(Fore.RED+conf.films.title +
                  " Error, the HDR poster for this film could not be created.")
            print(Fore.RESET)
            continue
else:
    print('Creating 4k posters only')
    for i in conf.films.search(resolution="4k"):
        try:
            poster_4k()
        except FileNotFoundError:
            print(Fore.RED+conf.films.title +
                  " Error, the 4k poster for this film could not be created.")
            print(Fore.RESET)
            continue

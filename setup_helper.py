from pathlib import Path
from PIL import Image
from plexapi.server import PlexServer
import numpy as np
import requests
import shutil
import os
import re
from configparser import ConfigParser
import platform
from colorama import Fore, Back, Style

config_object = ConfigParser()
config_object.read("config.ini")

server = config_object["PLEXSERVER"]
baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
films = plex.library.section(films)

print('This file will help you locate the media path that Plex sees.')
print('Running this will output a file location from your film library set in the config.ini')
print('It will only work properly if you have used the correct plex naming protocols.')
print('Searching...')

media_location = films.search(resolution='4k')
filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
print('Plex mount path is:')
print(filepath)

if platform.system() == 'Windows':
    print(Fore.CYAN + 'It looks like you are running this on Windows, your Mounted path should look like this:')
    print('"Z:/"')
    print('Take note of the forward slash here.') 
    print('It is important that you replace all backslashes with forward slashes for the script to work') 
    print(Fore.RESET)


print('checking poster download permissions...')
i = films.search(resolution='4k')
imgurl = i[0].posterUrl
img = requests.get(imgurl, stream=True)
if img.status_code == 200:
    print("You're good to go")
elif img.status_code == 401:
    print("Unable to download the image")

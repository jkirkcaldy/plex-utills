#!/usr/local/bin/python3
import os
import subprocess 
from configparser import ConfigParser
import subprocess
import schedule
import time
from datetime import datetime
from colorama import Fore, Back, Style
from plexapi.server import PlexServer
import requests


config_object = ConfigParser()
config_object.read("config/config.ini")
server = config_object["PLEXSERVER"]
schedules = config_object["SCHEDULES"]
options = config_object["OPTIONS"]

baseurl = (server["PLEX_URL"])
token = (server["TOKEN"])
films = (server["FILMSLIBRARY"])
plex = PlexServer(baseurl, token)
films = plex.library.section(films)

hdr_4k_posters = str.lower((options["4k_hdr_posters"]))
posters_3d_banner_add = str.lower((options["3d_posters"]))
Disney = str.lower((options["Disney"]))
Pixar = (str.lower(options["Pixar"]))
hide_4k = str.lower((options["hide_4k"]))

t1 = (schedules["4k_poster_schedule"])
t2 = (schedules["disney_schedule"])
t3 = (schedules["pixar_schedule"])
t4 = (schedules["hide_poster_schedule"])
t5 = (schedules["3d_poster_schedule"])

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

def check_config():
    p = subprocess.Popen('python -u ./config_check.py', shell=True, stderr=subprocess.STDOUT)
    output = p.communicate()
    print(output[0])

def posters_4k():
    if hdr_4k_posters == "true":
        p = subprocess.Popen('python -u ./4k_hdr_poster.py', shell=True)
        output = p.communicate()
        print(output[0])

def posters_3d():
    if posters_3d_banner_add == "true":
        p = subprocess.Popen('python -u ./4k_hdr_poster.py', shell=True)
        output = p.communicate()
        print(output[0])

def disney():
    if Disney == "true":
        p = subprocess.Popen('python -u ./disney_collection.py', shell=True)
        output = p.communicate()
        print(output[0])

def pixar():
    if Pixar == "true":
        p = subprocess.Popen('python -u ./Pixar_collection.py', shell=True)
        output = p.communicate()
        print(output[0])

def hide_4k_films():
    if hide_4k == "true":
        p = subprocess.Popen('python -u ./hide-4k.py', shell=True)
        output = p.communicate()
        print(output[0])        

def plex_file_path():
    media_location = films.search()
    filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
    print(Fore.GREEN, 'Plex mount path is:')
    print(filepath, Fore.RESET)
    print(Fore.LIGHTGREEN_EX, '# You should use the mount path of all your media not just your movies folder.', Fore.RESET)

    print(Fore.YELLOW, 'checking poster download permissions...')
    i = films.search(resolution='4k')
    imgurl = i[0].posterUrl
    img = requests.get(imgurl, stream=True)
    if img.status_code == 200:
        print(Fore.GREEN, "You're good to go", Fore.RESET)
    elif img.status_code == 401:
        print(Fore.RED, "Unable to download the image", Fore.RESET)

def working():
    print(current_time, ": This script is still working, check back later for more info")

print(current_time, ": This script is now running, check back later for more info")
check_config()
plex_file_path()
print('waiting for next script...')

schedule.every(60).minutes.do(working)
schedule.every().day.at(t1).do(posters_4k)
schedule.every().day.at(t5).do(posters_3d)   
schedule.every().day.at(t2).do(disney)
schedule.every().day.at(t3).do(pixar)
schedule.every().day.at(t4).do(hide_4k_films)

while True:
    schedule.run_pending()
    time.sleep(1)
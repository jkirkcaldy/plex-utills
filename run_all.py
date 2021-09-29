#!/usr/local/bin/python3
import os
from subprocess import Popen, PIPE, STDOUT
from configparser import ConfigParser
import schedule
import time
from datetime import datetime
from colorama import Fore, Back, Style
from plexapi.server import PlexServer
import requests
from colorama import Fore, Back, Style



now = datetime.now()
current_time = now.strftime("%H:%M:%S")

def check_config():
    p = Popen('python3 -u ./config_check.py', shell=True, stderr=STDOUT, stdout=PIPE)
    output = p.communicate()[0]

    if 'Pass' in str(output):
        print(Fore.LIGHTGREEN_EX,'Config check passed',Fore.RESET)
    else:
        exit()

#check_config()

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
mpath = (server["MOUNTEDPATH"])

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

def posters_4k():
    p = Popen('python -u ./4k_hdr_poster.py', shell=True)
    output = p.communicate()
    print(output[0])

def posters_3d():
    p = Popen('python -u ./4k_hdr_poster.py', shell=True)
    output = p.communicate()
    print(output[0])

def disney():
    p = Popen('python -u ./disney_collection.py', shell=True)
    output = p.communicate()
    print(output[0])

def pixar():
    p = Popen('python -u ./Pixar_collection.py', shell=True)
    output = p.communicate()
    print(output[0])

def hide_4k_films():
    p = Popen('python -u ./hide-4k.py', shell=True)
    output = p.communicate()
    print(output[0])        

def plex_file_path():
    media_location = films.search()
    filepath = os.path.dirname(os.path.dirname(media_location[0].media[0].parts[0].file))
    print(Fore.GREEN, 'Plex mount path is:')
    print('/'+filepath.split('/')[1], Fore.RESET)
    print(Fore.LIGHTYELLOW_EX, '# You should use the mount path of all your media not just your movies folder.', Fore.RESET)

    print(Fore.YELLOW, 'checking poster download permissions...')
    i = films.search()
    imgurl = i[0].posterUrl
    img = requests.get(imgurl, stream=True)
    if img.status_code == 200:
        print(Fore.GREEN, "You're good to go", Fore.RESET)
    elif img.status_code == 401:
        print(Fore.RED, "Unable to download the image", Fore.RESET)
def check_mpath():
    try:
        test_dir = os.listdir(mpath)
        print("if you see your media directories bellow then all should be good. If you don't see anything, or your don't see the expected directories make sure your plex media is mounted and mapped correctly in the config file.")
        print(Fore.LIGHTBLUE_EX, test_dir, Fore.RESET)
    except FileNotFoundError:
        print('Oops, it looks like', Fore.YELLOW,'"',mpath,'"', Fore.RESET, "isn't correct or doesn't have the right permissions")

def working():
    print(current_time, ": This script is still working, check back later for more info")

print(current_time, ": This script is now running, check back later for more info")
plex_file_path()
check_mpath()
print('waiting for next script...')
print('Your schedule is as follows:')



schedule.every(60).minutes.do(working)
if hdr_4k_posters == "true":
    print('4K HDR Posters:', t1)
    schedule.every().day.at(t1).do(posters_4k)
if posters_3d_banner_add == "true":
    print('3D banners:', t5)
    schedule.every().day.at(t5).do(posters_3d)  
if Disney == "true":
    print('Disney Collection:', t2)
    schedule.every().day.at(t2).do(disney)
if Pixar == "true":
    print('Pixar collection:', t3)
    schedule.every().day.at(t3).do(pixar)
if hide_4k == "true":
    print('Hide 4k Films:', t4)
    schedule.every().day.at(t4).do(hide_4k_films)

while True:
    schedule.run_pending()
    time.sleep(1)
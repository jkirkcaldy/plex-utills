#!/usr/local/bin/python3
import os
import subprocess 
from subprocess import Popen, PIPE, STDOUT
from configparser import ConfigParser
import subprocess
import plexapi
import schedule
import time
from datetime import datetime
import re
from colorama import Fore, Back, Style
import socket
from urllib import parse 
from plexapi.server import PlexServer

config_object = ConfigParser()
config_object.read("/config/config.ini")
server = config_object["PLEXSERVER"]
schedules = config_object["SCHEDULES"]
options = config_object["OPTIONS"]


hdr_4k_posters = str.lower((options["4k_hdr_posters"]))
poster_3d = str.lower((options["3D_posters"]))
Disney = str.lower((options["Disney"]))
Pixar = (str.lower(options["Pixar"]))
hide_4k = str.lower((options["hide_4k"]))
pbak = str.lower((options["POSTER_BU"]))
HDR_BANNER = str.lower((options["HDR_BANNER"]))
optimise = str.lower((options["transcode"]))
mini_4k = str.lower((options["mini_4k"]))
mini_3d = str.lower((options["mini_3D"]))

t1 = (schedules["4k_poster_schedule"])
t2 = (schedules["disney_schedule"])
t3 = (schedules["pixar_schedule"])
t4 = (schedules["hide_poster_schedule"])
t5 = (schedules["3d_poster_schedule"])

url = parse.urlparse(server["PLEX_URL"]).hostname
try: 
    url = parse.urlparse(server["PLEX_URL"]).hostname
    socket.inet_aton(url)
except socket.error:
    raise Exception("Uh-Oh, it looks like your PLEX_URL is not correct in the config file \n Make sure you enter it as 'http://ip-address:plex-port'")
if server["TOKEN"] == '<token>':
    raise Exception("You must add your Plex Token to the config file.")
try:
    print("Your Server's Friendly name is ", PlexServer((server["PLEX_URL"]), (server["TOKEN"])).friendlyName)
except :
    print('Cannot access your Plex account, please make sure that your Plex URL and Token are correct')
    exit()
if pbak == 'true':
    pass
elif pbak == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if HDR_BANNER == 'true':
    pass
elif HDR_BANNER == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if mini_4k == 'true':
    pass
elif mini_4k == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if hdr_4k_posters == 'true':
    pass
elif hdr_4k_posters == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if poster_3d == 'true':
    pass
elif poster_3d == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if Disney == 'true':
    pass
elif Disney == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if Pixar == 'true':
    pass
elif Pixar == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.') 

if hide_4k == 'true':
    pass
elif hide_4k == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.')    

if optimise == 'true':
    pass
elif optimise == 'false':
    pass
else:
    raise ValueError('SYNTAX ERROR: Please enter either "true" or "false" to set the script behaviour.')   



a = re.compile("^[0-9]{2}:[0-9]{2}$")
if a.match(t1) and hdr_4k_posters == 'true':
    pass
elif hdr_4k_posters != 'true':
    pass
else:
    raise ValueError('Please make sure that your scheduled times are written in the format HH:MM')
if a.match(t5) and poster_3d == 'true':
    pass
elif poster_3d != 'true':
    pass
else:
    raise ValueError('Please make sure that your scheduled times are written in the format HH:MM')     
if a.match(t2) and Disney == 'true':
    pass
elif Disney != 'true':
    pass
else:
    raise ValueError('Please make sure that your scheduled times are written in the format HH:MM') 
if a.match(t3) and Pixar == 'true':
    pass
elif Pixar != 'true':
    pass
else:
    raise ValueError('Please make sure that your scheduled times are written in the format HH:MM') 
if a.match(t4) and hide_4k == 'true':
    pass
elif hide_4k != 'true':
    pass
else:
    raise ValueError('Please make sure that your scheduled times are written in the format HH:MM')  

print('Config check passed')

p = Popen('python -u ./run_all.py', shell=True)
output = p.communicate()
print(output[0])
 
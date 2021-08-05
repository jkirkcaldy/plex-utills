#!/usr/local/bin/python3
import os
import subprocess 
from configparser import ConfigParser
import subprocess
import schedule
import time
from datetime import datetime
import re
from colorama import Fore, Back, Style


config_object = ConfigParser()
config_object.read("config/config.ini")
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
 
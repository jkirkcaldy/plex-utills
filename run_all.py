import os
import subprocess 
from configparser import ConfigParser
import subprocess
import schedule
import time
from datetime import datetime


config_object = ConfigParser()
config_object.read("/config/config.ini")
server = config_object["PLEXSERVER"]
schedules = config_object["SCHEDULES"]
hdr_4k_posters = (server["4k_hdr_posters"])
Disney = (server["Disney"])
Pixar = (server["Pixar"])
hide_4k = (server["hide_4k"])

t1 = (schedules["poster_schedule"])
t2 = (schedules["disney_schedule"])
t3 = (schedules["pixar_schedule"])
t4 = (schedules["hide_poster_schedule"])

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

def posters():
    if hdr_4k_posters == "True":
        p = subprocess.Popen('python -u ./4k_hdr_poster.py', shell=True)
        output = p.communicate()
        print(output[0])

def disney():
    if Disney == "True":
        p = subprocess.Popen('python -u ./disney_collection.py', shell=True)
        output = p.communicate()
        print(output[0])

def pixar():
    if Pixar == "True":
        p = subprocess.Popen('python -u ./Pixar_collection.py', shell=True)
        output = p.communicate()
        print(output[0])
def hide_4k_films():
    if hide_4k == "True":
        p = subprocess.Popen('python -u ./hide-4k.py', shell=True)
        output = p.communicate()
        print(output[0])        

def working():
    print(current_time, ": This script is still working, check back later for more info")

print(current_time, ": This script is now running, check back later for more info")

schedule.every(60).minutes.do(working)
schedule.every().day.at(t1).do(posters)   
schedule.every().day.at(t2).do(disney)
schedule.every().day.at(t3).do(pixar)
schedule.every().day.at(t4).do(hide_4k_films)

while True:
    schedule.run_pending()
    time.sleep(1)